# routers/bank_statements.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List
from db.database import get_db
from models.bank_statement import BankStatement, Transaction
from models.company import Company

router = APIRouter(prefix="/bank-statements", tags=["bank-statements"])

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id

@router.get("/")
def get_all_bank_statements(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Returns all bank statements for the current company."""
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    statements = db.query(BankStatement).join(
        BankStatement.document
    ).filter(
        BankStatement.document.has(company_id=company.id)
    ).order_by(BankStatement.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "account_number": s.account_number,
            "period": s.period,
            "opening_balance": s.opening_balance,
            "closing_balance": s.closing_balance,
        }
        for s in statements
    ]

@router.get("/{statement_id}/transactions")
def get_transactions(
    statement_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns all individual transactions within a bank statement.
    Used to show the detailed breakdown of debits and credits.
    """
    statement = db.query(BankStatement).filter(
        BankStatement.id == statement_id
    ).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Bank statement not found")

    return [
        {
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "amount": t.amount,
            "type": t.type
        }
        for t in statement.transactions
    ]