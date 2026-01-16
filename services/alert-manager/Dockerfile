# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder to system location
COPY --from=builder /root/.local /usr/local

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd -m -u 1000 alertmanager && chown -R alertmanager:alertmanager /app
USER alertmanager

# Set Python path for module imports
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PORT=8004

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

EXPOSE 8004

CMD ["python", "app/main.py"]