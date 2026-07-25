# models/financial.py
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    # Type of financial statement
    # "PnL" = Profit and Loss | "balance_sheet" | "cash_flow" | "budget"
    type = Column(String, nullable=False)

    # Period this statement covers e.g. "2026-Q2" or "2026-06"
    period = Column(String, nullable=True)

    # Key financial metrics extracted by AI from the document
    revenue = Column(Float, nullable=True)
    expenses = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)       # revenue - expenses

    # Balance sheet specific fields
    total_assets = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="financial_statement")