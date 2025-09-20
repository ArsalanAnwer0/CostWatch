FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Flask environment variables
ENV FLASK_APP=app.app
ENV FLASK_ENV=production
ENV PORT=8000

# Expose the port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health')"

# Run the application directly
CMD ["python", "app/app.py"]