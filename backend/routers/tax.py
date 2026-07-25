# routers/tax.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List
from db.database import get_db
from models.tax import TaxDocument
from models.company import Company
from schemas.tax import TaxDocumentResponse

router = APIRouter(prefix="/tax", tags=["tax"])

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id

@router.get("/", response_model=List[TaxDocumentResponse])
def get_all_tax_documents(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Returns all tax declarations for the current company."""
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    tax_docs = db.query(TaxDocument).join(
        TaxDocument.document
    ).filter(
        TaxDocument.document.has(company_id=company.id)
    ).order_by(TaxDocument.due_date.asc()).all()

    return tax_docs

@router.get("/overdue", response_model=List[TaxDocumentResponse])
def get_overdue_tax(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns unpaid tax declarations past their due date.
    These are high priority alerts — missing a tax deadline means penalties.
    """
    from datetime import date
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    overdue = db.query(TaxDocument).join(
        TaxDocument.document
    ).filter(
        TaxDocument.document.has(company_id=company.id),
        TaxDocument.status != "paid",
        TaxDocument.due_date < date.today()
    ).all()

    return overdue