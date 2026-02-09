from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from src.db import get_session
from src.models.report import Report, ReportCreate, ReportRead
from src.api.v1.auth import get_current_user
from src.models.user import User

router = APIRouter()


@router.post("/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Report a new civic issue"""
    db_report = Report.model_validate(report, update={"user_id": current_user.id})
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return db_report


@router.get("/reports", response_model=List[ReportRead])
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all reports submitted by the current user"""
    statement = select(Report).where(Report.user_id == current_user.id)
    results = session.exec(statement)
    return results.all()


@router.get("/public/reports", response_model=List[ReportRead])
async def get_all_reports(
    session: Session = Depends(get_session)
):
    """Public endpoint to see all civic issues for the transparency dashboard"""
    statement = select(Report)
    results = session.exec(statement)
    return results.all()
