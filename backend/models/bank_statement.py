# models/bank_statement.py
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from db.database import Base

class BankStatement(Base):
    __tablename__ = "bank_statements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    account_number = Column(String, nullable=True)
    period = Column(String, nullable=True)              # e.g. "2026-06"
    opening_balance = Column(Float, nullable=True)      # balance at start of period
    closing_balance = Column(Float, nullable=True)      # balance at end of period

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="bank_statement")
    transactions = relationship("Transaction", back_populates="bank_statement")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bank_statement_id = Column(String, ForeignKey("bank_statements.id"), nullable=False)

    date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)   # e.g. "Virement client ATLAS"
    amount = Column(Float, nullable=True)

    # "debit" = money going out | "credit" = money coming in
    type = Column(String, nullable=True)

    bank_statement = relationship("BankStatement", back_populates="transactions")