"""
Health check endpoint
No authentication required
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns server status and timestamp.
    No authentication required.

    Returns:
        dict: Status and timestamp
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}
