# Chat Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY services/chat/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/chat/src/ .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

EXPOSE 8001

CMD ["python", "main.py"]