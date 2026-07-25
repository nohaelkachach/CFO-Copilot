# routers/anomalies.py
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List

from db.database import get_db
from models.anomaly import Anomaly
from models.company import Company
from schemas.anomaly import AnomalyResponse, AnomalyResolve

router = APIRouter(
    prefix="/anomalies",
    tags=["anomalies"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session found.")
    return session_id


@router.get("/", response_model=List[AnomalyResponse])
def get_all_anomalies(
    session_id: str = Depends(get_session_id),
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Returns all anomalies detected for the current company.
    Optional filter: ?resolved=false to show only unresolved ones.
    This is the main feed the dashboard shows to alert the user.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    query = db.query(Anomaly).filter(Anomaly.company_id == company.id)

    # Optional filter — ?resolved=false shows only active anomalies
    if resolved is not None:
        query = query.filter(Anomaly.resolved == resolved)

    anomalies = query.order_by(
        Anomaly.resolved.asc(),      # unresolved first
        Anomaly.created_at.desc()    # newest first within each group
    ).all()

    return anomalies


@router.get("/unresolved/count")
def get_unresolved_count(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Returns the count of unresolved anomalies.
    Used by the dashboard header to show a badge like "3 anomalies"
    without loading all the full anomaly objects.
    """
    company = db.query(Company).filter(Company.session_id == session_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found for this session")

    count = db.query(Anomaly).filter(
        Anomaly.company_id == company.id,
        Anomaly.resolved == False
    ).count()

    return {"unresolved_count": count}


@router.patch("/{anomaly_id}/resolve", response_model=AnomalyResponse)
def resolve_anomaly(
    anomaly_id: str,
    request: AnomalyResolve,
    db: Session = Depends(get_db)
):
    """
    Marks an anomaly as resolved or unresolved.
    Called when the user reviews and addresses a flagged issue.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.resolved = request.resolved
    db.commit()
    db.refresh(anomaly)

    return anomaly


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly(
    anomaly_id: str,
    db: Session = Depends(get_db)
):
    """Returns a single anomaly by ID."""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return anomaly