#!/bin/bash

# CostWatch Development Environment Setup Script

set -e

echo " Setting up CostWatch development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo " Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo " docker-compose not found. Please install docker-compose."
    exit 1
fi

# Create necessary directories
echo " Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p nginx/ssl

# Generate self-signed SSL certificates for local development
if [ ! -f nginx/ssl/server.crt ]; then
    echo " Generating self-signed SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/server.key \
        -out nginx/ssl/server.crt \
        -subj "/C=US/ST=CA/L=SF/O=CostWatch/CN=localhost"
fi

# Set proper permissions
chmod 600 nginx/ssl/server.key
chmod 644 nginx/ssl/server.crt

# Create .env file for local development
if [ ! -f .env ]; then
    echo " Creating .env file..."
    cat > .env << EOF
# CostWatch Local Development Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://costwatch_user:costwatch_password@localhost:5432/costwatch
POSTGRES_DB=costwatch
POSTGRES_USER=costwatch_user
POSTGRES_PASSWORD=costwatch_password

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production

# AWS (Mock for development)
AWS_ACCESS_KEY_ID=mock-access-key
AWS_SECRET_ACCESS_KEY=mock-secret-key
AWS_DEFAULT_REGION=us-west-2

# Service URLs
RESOURCE_SCANNER_URL=http://localhost:5000
API_GATEWAY_URL=http://localhost:8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:80
EOF
fi

echo " Development environment setup completed!"
echo ""
echo " Next steps:"
echo "1. Run 'docker-compose up -d' to start all services"
echo "2. Visit http://localhost to access the application"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo "4. Use 'docker-compose logs -f' to view logs"
echo ""
echo "   Useful commands:"
echo "  docker-compose up -d        # Start all services"
echo "  docker-compose down         # Stop all services"
echo "  docker-compose logs -f      # View logs"
echo "  docker-compose restart      # Restart services"
echo "  docker-compose ps           # Check service status"