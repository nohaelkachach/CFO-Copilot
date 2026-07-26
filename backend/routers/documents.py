# routers/documents.py
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Cookie, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models import Document, Company
from schemas.document import DocumentResponse, DocumentUploadResponse
from services.document_service import process_document

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(
            status_code=401,
            detail="No session found. Please create a company first."
        )
    return session_id


def run_process_document(document_id: str, file_bytes: bytes):
    """
    Creates its own database session for background processing.
    Cannot reuse the request's session — it's already closed by the time
    background tasks run. This is a common FastAPI pattern for background tasks.
    """
    db = SessionLocal()
    try:
        process_document(document_id, file_bytes, db)
    except Exception as e:
        print(f"Background task error: {e}")
    finally:
        db.close()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Uploads a document (PDF or image).
    Returns immediately with document ID and pending status.
    AI processing (classification, anomaly detection) happens in background.
    """
    # Validate file type
    if not file.filename.endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and image files are supported."
        )

    # Get the company for this session
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="No company found for this session. Please create a company first."
        )

    # Read file bytes — needed for background processing
    file_bytes = await file.read()

    # Check if this filename was already uploaded for this company
    existing = db.query(Document).filter(
        Document.company_id == company.id,
        Document.filename == file.filename
    ).first()

    if existing:
        # File exists — reset and reprocess
        existing.processing_status = "pending"
        existing.extracted_text = None
        db.commit()
        document = existing
        message = f"Document '{file.filename}' already existed — reprocessing with new version."
    else:
        # New document — create fresh record
        document = Document(
            id=str(uuid.uuid4()),
            company_id=company.id,
            filename=file.filename,
            category="unknown",
            processing_status="pending"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        message = f"Document '{file.filename}' uploaded. AI processing started."

    # Start background processing with its own DB session
    background_tasks.add_task(
        run_process_document,
        document_id=document.id,
        file_bytes=file_bytes
    )

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        message=message
    )


@router.get("/{document_id}/status")
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the current processing status of a document.
    Frontend polls this every 2-3 seconds after upload
    until status is 'processed' or 'failed'.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.processing_status,
        "category": document.category if document.processing_status == "processed" else None
    }


@router.get("/", response_model=list[DocumentResponse])
def get_all_documents(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Returns all documents for the current session's company."""
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    documents = db.query(Document).filter(
        Document.company_id == company.id
    ).order_by(Document.uploaded_at.desc()).all()

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Returns a single document by ID."""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document