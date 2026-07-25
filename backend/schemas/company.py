# schemas/company.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CompanyCreate(BaseModel):
    """What the client sends when creating a company"""
    name: str
    sector: Optional[str] = None

class CompanyResponse(BaseModel):
    """What the API returns when querying a company"""
    id: str
    name: str
    sector: Optional[str]
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)  # allows converting SQLAlchemy model → Pydantic schema