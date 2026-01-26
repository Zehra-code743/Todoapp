"""
Dapr client configuration for the Advanced Todo application.
Sets up Dapr client for service invocation, state management, and pub/sub.
"""
import os
from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp
from contextlib import contextmanager
from typing import Generator


# Dapr configuration
DAPR_HOST = os.getenv("DAPR_HOST", "localhost")
DAPR_PORT = os.getenv("DAPR_PORT", "3500")


@contextmanager
def get_dapr_client() -> Generator[DaprClient, None, None]:
    """
    Context manager for Dapr client.
    Ensures proper cleanup of Dapr client resources.
    """
    with DaprClient() as client:
        yield client


def get_dapr_app(app):
    """
    Create a DaprApp wrapper for the FastAPI app.
    """
    return DaprApp(app)


# Global Dapr client instance (optional, for direct access)
# It's generally better to use the context manager approach
def create_global_dapr_client():
    """
    Create a global Dapr client instance.
    Note: Prefer using the context manager approach for better resource management.
    """
    return DaprClient()