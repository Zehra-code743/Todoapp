"""
Health check endpoint
No authentication required
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Liveness check endpoint

    Determines if backend pod is alive and functioning.
    Returns healthy status even if external dependencies are temporarily unavailable.

    Returns:
        dict: Health status and timestamp
    """
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint

    Determines if backend pod is ready to serve traffic.
    Checks database connection and MCP server status.

    Returns:
        dict: Readiness status with database and MCP server status
    """
    try:
        # Import here to avoid circular imports and for lazy loading
        from src.db import engine

        # Check database connection with lightweight query
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        # Database is connected
        database_status = "connected"
    except Exception:
        # Database connection failed
        database_status = "disconnected"

    # Check MCP server status
    # For now, assume MCP server is running if we can import the module
    # In a more complex setup, we might actually ping the MCP server
    try:
        # Check if MCP tools are available
        from src.api.v1 import chat
        mcp_server_status = "running"
    except Exception:
        mcp_server_status = "stopped"

    # Return 503 if any dependency is not ready
    if database_status == "disconnected" or mcp_server_status == "stopped":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not ready",
                "database": database_status,
                "mcp_server": mcp_server_status,
            }
        )

    return {
        "status": "ready",
        "database": database_status,
        "mcp_server": mcp_server_status,
    }
