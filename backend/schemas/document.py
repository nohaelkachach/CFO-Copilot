# schemas/document.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DocumentResponse(BaseModel):
    """What the API returns after a document is uploaded and processed"""
    id: str
    company_id: str
    filename: str
    category: str                    # "financial_statement" | "tax" | "audit"
    processing_status: str           # "pending" | "processing" | "processed" | "failed"
    extracted_text: Optional[str]    # raw text — might be None if still processing
    uploaded_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    """Immediate response after upload — before AI processing is done"""
    id: str
    filename: str
    message: str                     # e.g. "Document uploaded, AI processing started"