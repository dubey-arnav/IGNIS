# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_ROOT=/app \
    PYTHONPATH=/app:/app/backend \
    PORT=8000

WORKDIR /app

# Install system dependencies needed for compiling C-extensions (psycopg2, xgboost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install all dependencies (API + Automation)
COPY backend/requirements.txt /app/backend_requirements.txt
RUN pip install --no-cache-dir -r /app/backend_requirements.txt

# Copy application directories
COPY ml/ /app/ml/
COPY automation/ /app/automation/
COPY backend/ /app/backend/
COPY database/ /app/database/
COPY data/ /app/data/

EXPOSE 8000

# Support dynamic PORT environment variable (Hugging Face Spaces, Koyeb, Render, etc.)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir backend"]
