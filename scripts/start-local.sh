#!/bin/bash

# CostWatch Local Startup Script
# This script helps you quickly start CostWatch on your local machine

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   CostWatch Local Startup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker from https://www.docker.com/get-started"
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker is running
check_docker_running() {
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker Desktop or the Docker daemon"
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed"
        echo "Please install docker-compose from https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "docker-compose is installed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_warning ".env file not found"
        print_info "The docker-compose.yml file contains default environment variables"
        print_info "You can create a custom .env file if you need to override defaults"
    else
        print_success ".env file exists"
    fi
}

# Check for port conflicts
check_ports() {
    print_info "Checking for port conflicts..."

    PORTS=(80 5432 6379 8000 8001 8002 8003 8004)
    CONFLICTS=()

    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            CONFLICTS+=($port)
        fi
    done

    if [ ${#CONFLICTS[@]} -gt 0 ]; then
        print_warning "Port conflicts detected on: ${CONFLICTS[*]}"
        echo ""
        echo "You can either:"
        echo "  1. Stop services using these ports"
        echo "  2. Modify ports in docker-compose.yml"
        echo ""
        read -p "Do you want to continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "No port conflicts detected"
    fi
}

# Stop any existing containers
stop_existing() {
    print_info "Checking for existing CostWatch containers..."
    cd "$PROJECT_ROOT"

    if docker-compose ps -q | grep -q .; then
        print_warning "Found running CostWatch containers"
        read -p "Do you want to stop them first? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Stopping existing containers..."
            docker-compose down
            print_success "Stopped existing containers"
        fi
    else
        print_success "No existing containers running"
    fi
}

# Build containers
build_containers() {
    print_info "Building Docker containers..."
    cd "$PROJECT_ROOT"

    if docker-compose build; then
        print_success "Successfully built all containers"
    else
        print_error "Failed to build containers"
        exit 1
    fi
}

# Start containers
start_containers() {
    print_info "Starting CostWatch services..."
    cd "$PROJECT_ROOT"

    if docker-compose up -d; then
        print_success "Successfully started all services"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_info "Waiting for services to be ready..."
    cd "$PROJECT_ROOT"

    echo "This may take 1-2 minutes..."
    sleep 10

    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some containers failed to start"
        print_info "Check logs with: docker-compose logs"
        exit 1
    fi

    print_success "All containers are running"
}

# Show service URLs
show_urls() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}CostWatch is now running!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Access the application at:"
    echo ""
    echo -e "  ${GREEN}API Documentation:${NC}  http://localhost/docs"
    echo -e "  ${GREEN}API (ReDoc):${NC}       http://localhost/redoc"
    echo -e "  ${GREEN}Health Check:${NC}      http://localhost/health"
    echo ""
    echo "Direct service access:"
    echo ""
    echo -e "  API Gateway:        http://localhost:8002"
    echo -e "  Resource Scanner:   http://localhost:8000"
    echo -e "  Cost Analyzer:      http://localhost:8001"
    echo -e "  Analytics Engine:   http://localhost:8003"
    echo -e "  Alert Manager:      http://localhost:8004"
    echo ""
    echo "Database connections:"
    echo ""
    echo -e "  PostgreSQL:         localhost:5432 (costwatch/costwatch_user)"
    echo -e "  Redis:              localhost:6379"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Useful commands:"
    echo ""
    echo -e "  View logs:          ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  Stop services:      ${YELLOW}docker-compose down${NC}"
    echo -e "  Restart service:    ${YELLOW}docker-compose restart <service-name>${NC}"
    echo -e "  View status:        ${YELLOW}docker-compose ps${NC}"
    echo ""
    echo -e "${GREEN}For detailed documentation, see docs/LOCAL_SETUP.md${NC}"
    echo ""
}

# Offer to show logs
show_logs_prompt() {
    echo ""
    read -p "Do you want to follow the logs now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Following logs (press Ctrl+C to exit)..."
        cd "$PROJECT_ROOT"
        docker-compose logs -f
    fi
}

# Main execution
main() {
    echo "Step 1: Checking prerequisites..."
    check_docker
    check_docker_running
    check_docker_compose
    check_env_file
    echo ""

    echo "Step 2: Checking ports..."
    check_ports
    echo ""

    echo "Step 3: Preparing environment..."
    stop_existing
    echo ""

    echo "Step 4: Building containers..."
    build_containers
    echo ""

    echo "Step 5: Starting services..."
    start_containers
    echo ""

    echo "Step 6: Waiting for services..."
    wait_for_services
    echo ""

    show_urls
    show_logs_prompt
}

# Handle script interruption
trap 'echo ""; print_warning "Script interrupted"; exit 130' INT

# Run main function
main
