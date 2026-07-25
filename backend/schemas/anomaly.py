# schemas/anomaly.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnomalyResponse(BaseModel):
    id: str
    company_id: str
    document_id: str
    description: str                 # "Invoice #1047 is 40% above average"
    severity: str                    # "low" | "medium" | "high"
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AnomalyResolve(BaseModel):
    """What the client sends to mark an anomaly as resolved"""
    resolved: bool = True