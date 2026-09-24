# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_ROOT=/app \
    PYTHONPATH=/app:/app/backend \
    PORT=7860

WORKDIR /app

# Install system dependencies needed for psycopg2, xgboost, and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install all dependencies (API + Automation)
COPY backend/requirements.txt /app/backend_requirements.txt
RUN pip install --no-cache-dir -r /app/backend_requirements.txt

# Create a non-root user (UID 1000 is required by Hugging Face Spaces)
RUN useradd -m -u 1000 user && \
    mkdir -p /app/automation/logs && \
    chown -R user:user /app

# Copy application directories with proper ownership
COPY --chown=user:user ml/ /app/ml/
COPY --chown=user:user automation/ /app/automation/
COPY --chown=user:user backend/ /app/backend/
COPY --chown=user:user database/ /app/database/
COPY --chown=user:user data/ /app/data/

USER 1000

EXPOSE 7860

# Run uvicorn on $PORT (defaults to 7860 for HF Spaces, or whatever cloud platform injects)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --app-dir backend"]
