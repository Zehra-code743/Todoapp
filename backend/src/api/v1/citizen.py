from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from src.db import get_session
from src.models.report import Report, ReportCreate, ReportRead
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter()


@router.post("/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Report a new civic issue"""
    db_report = Report.model_validate(report, update={"user_id": current_user_id})
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return db_report


@router.get("/reports", response_model=List[ReportRead])
async def get_my_reports(
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all reports submitted by the current user"""
    statement = select(Report).where(Report.user_id == current_user_id)
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


@router.post("/reports/summarize", tags=["AI"])
async def summarize_reports(
    category: Optional[str] = None,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    AI Placeholder: Summarize civic issues for a category using LLM.
    In a real implementation, this would fetch reports and use GPT-4/Claude to generate a summary.
    """
    # Placeholder logic
    return {
        "summary": "AI Summarization is currently in development. Soon you will see generated insights here.",
        "category_analyzed": category or "all",
        "status": "placeholder"
    }
