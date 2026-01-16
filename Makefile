.PHONY: help build up down logs clean test health

# Default target
help:
	@echo "CostWatch Makefile Commands:"
	@echo ""
	@echo "  make build       - Build all Docker containers"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Remove all containers, images, and volumes"
	@echo "  make test        - Run health checks"
	@echo "  make health      - Check service health"
	@echo "  make restart     - Restart all services"
	@echo "  make shell-api   - Open shell in API Gateway"
	@echo "  make shell-db    - Open PostgreSQL shell"
	@echo ""

# Build all containers
build:
	@echo "Building all Docker containers..."
	docker-compose build

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@make health

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	@echo "Cleaning up Docker resources..."
	@./scripts/clean-docker.sh

# Run health checks
health:
	@echo "Checking service health..."
	@./scripts/test-health.sh

# Restart all services
restart:
	@echo "Restarting services..."
	docker-compose restart

# Open shell in API Gateway
shell-api:
	docker-compose exec api-gateway /bin/sh

# Open PostgreSQL shell
shell-db:
	docker-compose exec postgres psql -U costwatch_user -d costwatch

# Run tests (when implemented)
test:
	@echo "Running tests..."
	@echo "Tests not yet implemented"

# Quick start (build and run)
start: build up

# Full reset (clean and restart)
reset: clean build up
