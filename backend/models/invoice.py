# models/invoice.py
from sqlalchemy import Column, String, Float, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    invoice_number = Column(String, nullable=True)   # e.g. "FAC-2026-0847"
    vendor = Column(String, nullable=True)           # supplier or client name
    amount = Column(Float, nullable=True)            # total amount
    date = Column(Date, nullable=True)               # invoice date
    due_date = Column(Date, nullable=True)           # payment due date
    is_paid = Column(Boolean, default=False)         # has this been paid?

    # "received" = invoice from a supplier (we owe money)
    # "issued" = invoice we sent to a client (they owe us money)
    direction = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="invoice")