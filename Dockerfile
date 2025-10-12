# Dashboard Builder MVP Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cloud_run_mvp.py .
COPY real_google_sheets_extractor.py .
COPY google_sheets_service.py .
COPY config.py .
COPY gunicorn.conf.py .
COPY date_normalizer.py .
COPY bigquery_firestore_manager.py .
# Credenciais agora são baixadas do Google Cloud Storage
COPY static/ ./static/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application with Gunicorn for production
CMD ["gunicorn", "--config", "gunicorn.conf.py", "cloud_run_mvp:app"]
