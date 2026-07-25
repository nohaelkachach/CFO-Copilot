# routers/financial.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from db.database import get_db
from models.financial import FinancialStatement
from models.company import Company
from schemas.financial import FinancialStatementResponse, FinancialSummary

router = APIRouter(
    prefix="/financial",
    tags=["financial"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id


@router.get("/", response_model=List[FinancialStatementResponse])
def get_all_financial_statements(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns all financial statements for the current company.
    Includes P&L, balance sheets, cash flow statements, budgets.
    Ordered by most recent first.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    statements = db.query(FinancialStatement).join(
        FinancialStatement.document
    ).filter(
        FinancialStatement.document.has(company_id=company.id)
    ).order_by(FinancialStatement.created_at.desc()).all()

    return statements


@router.get("/summary", response_model=List[FinancialSummary])
def get_financial_summary(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns a lightweight summary of all financial statements.
    Used by the dashboard KPI cards — only key metrics, no heavy fields.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    statements = db.query(FinancialStatement).join(
        FinancialStatement.document
    ).filter(
        FinancialStatement.document.has(company_id=company.id)
    ).all()

    return statements


@router.get("/pnl")
def get_pnl_overview(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated P&L data across all periods.
    Used by the frontend to render the revenue vs expenses chart.
    Returns data grouped by period so the chart can plot a timeline.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    statements = db.query(FinancialStatement).join(
        FinancialStatement.document
    ).filter(
        FinancialStatement.document.has(company_id=company.id),
        FinancialStatement.type == "PnL"
    ).order_by(FinancialStatement.period.asc()).all()

    # Format for frontend chart consumption
    # Each item = one bar/point on the chart
    return [
        {
            "period": s.period,
            "revenue": s.revenue,
            "expenses": s.expenses,
            "net_profit": s.net_profit,
        }
        for s in statements
    ]


@router.get("/balance-sheet/latest")
def get_latest_balance_sheet(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns the most recent balance sheet.
    Shows total assets vs total liabilities — key for financial health overview.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    balance_sheet = db.query(FinancialStatement).join(
        FinancialStatement.document
    ).filter(
        FinancialStatement.document.has(company_id=company.id),
        FinancialStatement.type == "balance_sheet"
    ).order_by(FinancialStatement.created_at.desc()).first()

    if not balance_sheet:
        raise HTTPException(
            status_code=404,
            detail="No balance sheet found. Upload a balance sheet document first."
        )

    return {
        "period": balance_sheet.period,
        "total_assets": balance_sheet.total_assets,
        "total_liabilities": balance_sheet.total_liabilities,
        "equity": (balance_sheet.total_assets or 0) - (balance_sheet.total_liabilities or 0)
        # equity = assets - liabilities — fundamental accounting equation
    }


@router.get("/{statement_id}", response_model=FinancialStatementResponse)
def get_financial_statement(
    statement_id: str,
    db: Session = Depends(get_db)
):
    """Returns a single financial statement by ID."""
    statement = db.query(FinancialStatement).filter(
        FinancialStatement.id == statement_id
    ).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Financial statement not found")

    return statement