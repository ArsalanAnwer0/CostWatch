#!/bin/bash

# Health Check Test Script
# Tests all CostWatch service health endpoints

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing CostWatch Service Health Endpoints..."
echo ""

# Test Resource Scanner
echo -n "Resource Scanner (8000): "
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Test Cost Analyzer
echo -n "Cost Analyzer (8001): "
if curl -f -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Test API Gateway
echo -n "API Gateway (8002): "
if curl -f -s http://localhost:8002/health > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Test Analytics Engine
echo -n "Analytics Engine (8003): "
if curl -f -s http://localhost:8003/health > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Test Alert Manager
echo -n "Alert Manager (8004): "
if curl -f -s http://localhost:8004/health > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Test Frontend
echo -n "Frontend (3000): "
if curl -f -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy or no health endpoint${NC}"
fi

echo ""
echo "Health check complete!"
