# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from db.database import get_db
from models.company import Company
from models.document import Document
from services.ai_service import answer_financial_question  # we'll build this
from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id


@router.post("/", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Natural language question answering over the company's financial documents.
    Two modes:
    1. document_id provided → answer from that specific document only
    2. no document_id → answer from all processed documents (RAG over the whole corpus)
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    if request.document_id:
        # Mode 1 — answer from a specific document
        document = db.query(Document).filter(
            Document.id == request.document_id,
            Document.company_id == company.id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.processing_status != "processed":
            raise HTTPException(
                status_code=400,
                detail="Document is still being processed. Please wait and try again."
            )

        context = document.extracted_text
        sources = [document.filename]

    else:
        # Mode 2 — answer from all processed documents (RAG)
        documents = db.query(Document).filter(
            Document.company_id == company.id,
            Document.processing_status == "processed"
        ).all()

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No processed documents found. Please upload some documents first."
            )

        # Combine all extracted text as context
        # In production this would use vector search (RAG) instead of
        # concatenating everything — but for v1 this works for small document sets
        context = "\n\n---\n\n".join([
            f"Document: {doc.filename}\n{doc.extracted_text}"
            for doc in documents
            if doc.extracted_text
        ])
        sources = [doc.filename for doc in documents]

    # Send question + context to AI
    answer = answer_financial_question(
        question=request.question,
        context=context
    )

    return ChatResponse(answer=answer, sources=sources)