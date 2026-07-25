# models/tax.py
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class TaxDocument(Base):
    __tablename__ = "tax_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    # Type of tax declaration
    # "TVA" = VAT | "IS" = corporate tax | "CNSS" = social contributions | "IR" = income tax
    type = Column(String, nullable=False)

    period = Column(String, nullable=True)       # e.g. "2026-06"
    amount_due = Column(Float, nullable=True)    # what the company owes
    amount_paid = Column(Float, nullable=True)   # what was actually paid
    due_date = Column(Date, nullable=True)       # legal deadline

    # "paid" | "unpaid" | "late" — late means due_date has passed and still unpaid
    status = Column(String, default="unpaid")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="tax_document")