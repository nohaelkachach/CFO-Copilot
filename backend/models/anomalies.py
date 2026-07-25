# models/anomaly.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    # Human-readable description of what the AI flagged
    # e.g. "Invoice #1047 is 40% above average for this vendor"
    description = Column(String, nullable=False)

    # "low" | "medium" | "high" — how serious is this anomaly?
    severity = Column(String, default="medium")

    # Has the user acknowledged or resolved this anomaly?
    resolved = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="anomalies")
    document = relationship("Document", back_populates="anomalies")