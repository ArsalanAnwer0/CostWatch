FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN useradd -m -u 1000 alertmanager && chown -R alertmanager:alertmanager /app
USER alertmanager

ENV PORT=8004

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

EXPOSE 8004

CMD ["python", "app/main.py"]