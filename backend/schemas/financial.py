# schemas/financial.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class FinancialStatementResponse(BaseModel):
    id: str
    document_id: str
    type: str                        # "PnL" | "balance_sheet" | "cash_flow"
    period: Optional[str]            # "2026-Q2"
    revenue: Optional[float]
    expenses: Optional[float]
    net_profit: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)

class FinancialSummary(BaseModel):
    """Lightweight version for dashboard display — no heavy fields"""
    type: str
    period: Optional[str]
    net_profit: Optional[float]
    revenue: Optional[float]