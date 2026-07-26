# core/models.py
# Pydantic models for AI service outputs
# These define exactly what the AI must return — validated automatically

from typing import Optional
from pydantic import BaseModel, Field


class DocumentClassification(BaseModel):
    category: str = Field(description="financial_statement | tax | audit")
    type: str = Field(description="PnL | balance_sheet | invoice | TVA etc")
    period: Optional[str] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    currency: Optional[str] = Field(default="MAD")
    date: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None)
    direction: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.0, ge=0, le=1)
    # Financial statement specific fields
    revenue: Optional[float] = Field(default=None)
    expenses: Optional[float] = Field(default=None)
    net_profit: Optional[float] = Field(default=None)
    total_assets: Optional[float] = Field(default=None)
    total_liabilities: Optional[float] = Field(default=None)
    closing_balance: Optional[float] = Field(default=None)

class AnomalyItem(BaseModel):
    """A single anomaly detected by the AI auditor."""
    description: str
    severity: str = Field(description="low | medium | high")
    document_hint: Optional[str] = Field(default=None)


class FinancialAnswer(BaseModel):
    """Response from financial Q&A."""
    answer: str
    sources: list[str] = Field(default_factory=list)