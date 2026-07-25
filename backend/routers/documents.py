# routers/documents.py
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Cookie, BackgroundTasks
from sqlalchemy.orm import Session
import pdfplumber
import io

from db.database import get_db
from models.document import Document
from models.company import Company
from schemas.document import DocumentResponse, DocumentUploadResponse
from services.ai_service import classify_document  

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


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Parses a PDF and extracts all text content.
    Uses pdfplumber — reliable for text-based PDFs.
    For scanned PDFs (images), OCR would be needed (future improvement).
    """
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def process_document_in_background(
    document_id: str,
    file_bytes: bytes,
    db: Session
):
    """
    This runs in the background after the upload endpoint returns.
    Steps:
    1. Extract text from PDF
    2. Send text to LLM for classification
    3. Save results to database
    4. Update processing_status to "processed" or "failed"
    """
    # Get the document from DB
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return

    try:
        # Step 1 — Parse PDF and extract raw text
        document.processing_status = "processing"
        db.commit()

        extracted_text = extract_text_from_pdf(file_bytes)
        document.extracted_text = extracted_text

        # Step 2 — Send to AI for classification and field extraction
        # classify_document returns a dict with type, category, and extracted fields
        ai_result = classify_document(extracted_text)

        # Step 3 — Save classification result
        document.category = ai_result.get("category", "audit")
        document.processing_status = "processed"
        db.commit()

        # Step 4 — Save to the correct child table based on category
        # (we'll add this logic when we build the AI service)

    except Exception as e:
        # If anything fails, mark as failed so the user knows
        document.processing_status = "failed"
        db.commit()
        print(f"Document processing failed: {e}")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Uploads a document (PDF or image).
    Returns immediately with a document ID and "pending" status.
    AI processing happens in the background.
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

    # Read file bytes — we need them for parsing
    file_bytes = await file.read()

    # Check if this filename was already uploaded for this company
    existing = db.query(Document).filter(
        Document.company_id == company.id,
        Document.filename == file.filename
    ).first()

    if existing:
        # File already exists — update it instead of creating a new one
        existing.processing_status = "pending"
        existing.extracted_text = None  # will be re-extracted
        db.commit()
        document = existing
        message = f"Document '{file.filename}' already existed — reprocessing with new version."
    else:
        # New document — create a fresh record
        document = Document(
            id=str(uuid.uuid4()),
            company_id=company.id,
            filename=file.filename,
            category="unknown",          # AI will determine this in background
            processing_status="pending"  # will be updated by background task
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        message = f"Document '{file.filename}' uploaded successfully. AI processing started."

    # Start AI processing in the background — don't make the user wait
    # BackgroundTasks runs after the response is sent to the client
    background_tasks.add_task(
        process_document_in_background,
        document_id=document.id,
        file_bytes=file_bytes,
        db=db
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
    Frontend polls this endpoint every 2-3 seconds after upload
    until status is "processed" or "failed".
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
    """
    Returns all documents for the current session's company.
    """
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
    """
    Returns a single document by ID including extracted text and category.
    Only useful after processing_status = "processed".
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document