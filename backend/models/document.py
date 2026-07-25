# models/document.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    filename = Column(String, nullable=False)

    # category tells us which child table this document extends
    # "financial_statement" | "tax" | "audit"
    category = Column(String, nullable=False)

    # processing_status tracks where we are in the AI pipeline
    # "pending" → "processing" → "processed" | "failed"
    processing_status = Column(String, default="pending")

    # Raw text extracted from the PDF by the AI — stored for querying later
    extracted_text = Column(Text, nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="documents")
    financial_statement = relationship("FinancialStatement", back_populates="document", uselist=False)
    tax_document = relationship("TaxDocument", back_populates="document", uselist=False)
    invoice = relationship("Invoice", back_populates="document", uselist=False)
    bank_statement = relationship("BankStatement", back_populates="document", uselist=False)
    anomalies = relationship("Anomaly", back_populates="document")