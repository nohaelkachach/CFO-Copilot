# routers/invoices.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List

from db.database import get_db
from models.invoice import Invoice
from models.company import Company
from schemas.invoice import InvoiceResponse

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id


@router.get("/", response_model=List[InvoiceResponse])
def get_all_invoices(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Returns all invoices for the current company."""
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    invoices = db.query(Invoice).join(
        Invoice.document
    ).filter(
        Invoice.document.has(company_id=company.id)
    ).order_by(Invoice.date.desc()).all()

    return invoices


@router.get("/unpaid", response_model=List[InvoiceResponse])
def get_unpaid_invoices(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns only unpaid invoices — used for the late payment alerts feature.
    Frontend shows these as red flags on the dashboard.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    unpaid = db.query(Invoice).join(
        Invoice.document
    ).filter(
        Invoice.document.has(company_id=company.id),
        Invoice.is_paid == False
    ).order_by(Invoice.due_date.asc()).all()  # sorted by urgency — soonest due first

    return unpaid


@router.patch("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
def mark_invoice_paid(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """
    Marks an invoice as paid.
    Called when the user confirms a payment was received or made.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.is_paid = True
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """Returns a single invoice by ID."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice