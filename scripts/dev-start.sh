#!/bin/bash

# CostWatch Development Startup Script

set -e

echo " Starting CostWatch development environment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start services
echo " Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo " Waiting for services to be ready..."
sleep 10

# Check service health
echo " Checking service health..."

# Check API Gateway
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo " API Gateway is healthy"
else
    echo " API Gateway is not responding"
fi

# Check Resource Scanner
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo " Resource Scanner is healthy"
else
    echo " Resource Scanner is not responding"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U costwatch_user > /dev/null 2>&1; then
    echo " PostgreSQL is healthy"
else
    echo " PostgreSQL is not responding"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo " Redis is healthy"
else
    echo " Redis is not responding"
fi

echo ""
echo " CostWatch development environment is ready!"
echo ""
echo " Available endpoints:"
echo "  Main Application:  http://localhost"
echo "  API Gateway:       http://localhost:8000"
echo "  Resource Scanner:  http://localhost:5000"
echo "  API Documentation: http://localhost:8000/docs"
echo "  PostgreSQL:        localhost:5432"
echo "  Redis:             localhost:6379"
echo ""
echo " View logs with: docker-compose logs -f"