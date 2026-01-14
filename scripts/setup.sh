#!/bin/bash

# CostWatch Development Environment Setup Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}$1${NC}"; }
warn() { echo -e "${YELLOW}$1${NC}"; }

log "Setting up CostWatch development environment..."

# Check prerequisites
command -v python3 &> /dev/null || { echo "Python 3.11+ required"; exit 1; }
command -v docker &> /dev/null || { echo "Docker required"; exit 1; }

# Setup Python environments for each service
for service in api-gateway cost-analyzer resource-scanner analytics-engine alert-manager; do
    log "Setting up $service..."
    cd services/$service
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    cd ../..
done

# Start infrastructure with Docker Compose
log "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for database
sleep 5

# Initialize database
log "Initializing database..."
psql -h localhost -U postgres -c "CREATE DATABASE costwatch_dev;" || true
psql -h localhost -U postgres -d costwatch_dev -f database/schemas/01_init.sql
psql -h localhost -U postgres -d costwatch_dev -f database/schemas/02_tables.sql
psql -h localhost -U postgres -d costwatch_dev -f database/schemas/04_performance_indexes.sql
psql -h localhost -U postgres -d costwatch_dev -f database/schemas/05_constraints.sql
psql -h localhost -U postgres -d costwatch_dev -f database/schemas/06_views.sql

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    log "Creating .env file..."
    cat > .env << 'ENV_EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/costwatch_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=dev-secret-key-change-in-production
AWS_REGION=us-west-2
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ENV_EOF
fi

log "Setup complete! Start services with:"
echo "  cd services/api-gateway && source venv/bin/activate && uvicorn app.main:app --reload --port 8002"
