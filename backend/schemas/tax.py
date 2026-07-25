# schemas/tax.py

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class TaxDocumentResponse(BaseModel):
    id: str
    document_id: str
    type: str                        # "TVA" | "IS" | "CNSS" | "IR"
    period: Optional[str]
    amount_due: Optional[float]
    amount_paid: Optional[float]
    due_date: Optional[date]
    status: str                      # "paid" | "unpaid" | "late"
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)