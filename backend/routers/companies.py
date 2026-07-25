# routers/companies.py
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db
from models.company import Company
from schemas.company import CompanyCreate, CompanyResponse

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    """
    Reads the session_id cookie from the request.
    If no cookie exists yet, generates a new UUID.
    This lets us track which company belongs to which browser session
    without requiring user authentication.
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(
    request: CompanyCreate,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Creates a new company and sets a session cookie.
    The session_id links this company to the current browser session.
    """
    # Check if a company already exists for this session
    # One session = one company for simplicity
    existing = db.query(Company).filter(Company.session_id == session_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A company already exists for this session. Use GET /companies/me to retrieve it."
        )

    # Create the new company
    company = Company(
        id=str(uuid.uuid4()),
        name=request.name,
        sector=request.sector,
        session_id=session_id  # link company to this browser session
    )

    db.add(company)
    db.commit()
    db.refresh(company)  # refresh to get server-generated fields like created_at

    # Set the session cookie so the browser remembers this session
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,   # not accessible via JavaScript — more secure
        max_age=86400    # cookie lasts 24 hours (in seconds)
    )

    return company


@router.get("/me", response_model=CompanyResponse)
def get_my_company( session_id: str = Depends(get_session_id), db: Session = Depends(get_db)):
    """
    Returns the company associated with the current browser session.
    Used by the frontend to load the company's data on page refresh.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="No company found for this session. Please create one first."
        )

    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns a company by its ID.
    Used internally when we already know the company_id.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company