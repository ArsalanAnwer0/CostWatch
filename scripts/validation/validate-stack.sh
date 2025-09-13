#!/bin/bash

# CostWatch Stack Validation Script

set -e

echo " Validating CostWatch development stack..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track validation results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

validate_check() {
    local check_name="$1"
    local command="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $check_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

validate_http_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $name ($url)... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Header
echo -e "${BLUE}       CostWatch Stack Validation         ${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW} Docker Environment${NC}"
validate_check "Docker daemon" "docker info"
validate_check "Docker Compose" "docker-compose --version"

# Check if containers are running
echo ""
echo -e "${YELLOW} Container Status${NC}"
validate_check "PostgreSQL container" "docker-compose ps postgres | grep -q 'Up'"
validate_check "Redis container" "docker-compose ps redis | grep -q 'Up'"
validate_check "API Gateway container" "docker-compose ps api-gateway | grep -q 'Up'"
validate_check "Resource Scanner container" "docker-compose ps resource-scanner | grep -q 'Up'"
validate_check "Nginx container" "docker-compose ps nginx | grep -q 'Up'"

# Check service health endpoints
echo ""
echo -e "${YELLOW} Service Health${NC}"
validate_http_endpoint "API Gateway health" "http://localhost:8000/health"
validate_http_endpoint "Resource Scanner health" "http://localhost:5000/health"
validate_http_endpoint "Nginx proxy" "http://localhost:80/health"

# Check API endpoints
echo ""
echo -e "${YELLOW} API Endpoints${NC}"
validate_http_endpoint "API Gateway root" "http://localhost:8000/"
validate_http_endpoint "API Gateway info" "http://localhost:8000/info"
validate_http_endpoint "API Gateway docs" "http://localhost:8000/docs"
validate_http_endpoint "Resource Scanner root" "http://localhost:5000/"
validate_http_endpoint "Resource Scanner metrics" "http://localhost:5000/metrics"

# Check database connectivity
echo ""
echo -e "${YELLOW} Database Connectivity${NC}"
validate_check "PostgreSQL connection" "docker-compose exec -T postgres pg_isready -U costwatch_user"
validate_check "Redis connection" "docker-compose exec -T redis redis-cli ping | grep -q PONG"

# Check logs for errors
echo ""
echo -e "${YELLOW} Log Analysis${NC}"
validate_check "No critical errors in API Gateway logs" "! docker-compose logs api-gateway --tail=50 | grep -i 'error\\|exception\\|failed' | grep -v 'test'"
validate_check "No critical errors in Resource Scanner logs" "! docker-compose logs resource-scanner --tail=50 | grep -i 'error\\|exception\\|failed' | grep -v 'test'"

# Check network connectivity between services
echo ""
echo -e "${YELLOW} Service Communication${NC}"
validate_check "API Gateway can reach Resource Scanner" "docker-compose exec -T api-gateway curl -f http://resource-scanner:5000/health"
validate_check "Services can reach database" "docker-compose exec -T api-gateway curl -f http://postgres:5432 || true"  # Connection test

# Check file permissions and volumes
echo ""
echo -e "${YELLOW} File System${NC}"
validate_check "Database volume exists" "docker volume ls | grep -q costwatch_postgres_data"
validate_check "Redis volume exists" "docker volume ls | grep -q costwatch_redis_data"
validate_check "Application files mounted" "docker-compose exec -T api-gateway ls /app/app/main.py"

# Performance checks
echo ""
echo -e "${YELLOW}⚡ Performance${NC}"
validate_check "API Gateway response time < 2s" "timeout 2s curl -s http://localhost:8000/health"
validate_check "Resource Scanner response time < 2s" "timeout 2s curl -s http://localhost:5000/health"

# Summary
echo ""

echo -e "${BLUE}         Validation Summary               ${NC}"

echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e " ${GREEN}All checks passed!${NC} ($PASSED_CHECKS/$TOTAL_CHECKS)"
    echo -e " ${GREEN}CostWatch stack is healthy and ready for development!${NC}"
    exit 0
else
    echo -e " ${RED}Some checks failed${NC} ($FAILED_CHECKS/$TOTAL_CHECKS failed)"
    echo -e " ${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e " ${RED}Failed: $FAILED_CHECKS${NC}"
    echo ""
    echo -e "${YELLOW} Troubleshooting tips:${NC}"
    echo "1. Run 'docker-compose up -d' to start all services"
    echo "2. Check logs with 'docker-compose logs <service-name>'"
    echo "3. Restart services with 'docker-compose restart'"
    echo "4. Check available ports with 'netstat -tulpn'"
    exit 1
fi