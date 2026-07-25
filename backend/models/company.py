# models/company.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class Company(Base):
    __tablename__ = "companies"

    # UUID is better than Integer for IDs in production — harder to guess, globally unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    sector = Column(String, nullable=True)  # retail, construction, services etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(String, nullable=True, index=True)
    # Relationships — SQLAlchemy uses these to let you do company.documents
    # instead of writing a JOIN query manually
    documents = relationship("Document", back_populates="company")
    anomalies = relationship("Anomaly", back_populates="company")