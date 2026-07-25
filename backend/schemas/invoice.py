# schemas/invoice.py

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class InvoiceResponse(BaseModel):
    id: str
    document_id: str
    invoice_number: Optional[str]
    vendor: Optional[str]
    amount: Optional[float]
    date: Optional[date]
    due_date: Optional[date]
    is_paid: bool
    direction: Optional[str]         # "received" | "issued"
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)