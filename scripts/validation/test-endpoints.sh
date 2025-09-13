#!/bin/bash

# CostWatch API Endpoints Testing Script

set -e

echo " Testing CostWatch API endpoints..."

# Configuration
API_GATEWAY_URL="http://localhost:8000"
RESOURCE_SCANNER_URL="http://localhost:5000"
TEST_EMAIL="test_$(date +%s)@costwatch.com"
TEST_PASSWORD="testpassword123"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0

test_endpoint() {
    local test_name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local auth_header="$5"
    local expected_status="${6:-200}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing $test_name... "
    
    # Build curl command
    local curl_cmd="curl -s -o /tmp/test_response -w '%{http_code}'"
    
    if [ -n "$auth_header" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $auth_header'"
    fi
    
    if [ "$method" = "POST" ]; then
        curl_cmd="$curl_cmd -X POST -H 'Content-Type: application/json'"
        if [ -n "$data" ]; then
            curl_cmd="$curl_cmd -d '$data'"
        fi
    fi
    
    curl_cmd="$curl_cmd '$url'"
    
    # Execute request
    if response_code=$(eval "$curl_cmd" 2>/dev/null); then
        if [ "$response_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $response_code)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (HTTP $response_code, expected $expected_status)"
            if [ -f /tmp/test_response ]; then
                echo "Response: $(cat /tmp/test_response)"
            fi
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Start testing

echo -e "${BLUE}    CostWatch API Endpoint Tests       ${NC}"

echo ""

# Basic health checks
echo -e "${YELLOW} Health Checks${NC}"
test_endpoint "API Gateway Health" "GET" "$API_GATEWAY_URL/health"
test_endpoint "Resource Scanner Health" "GET" "$RESOURCE_SCANNER_URL/health"

# API Gateway basic endpoints
echo ""
echo -e "${YELLOW} API Gateway Basic Endpoints${NC}"
test_endpoint "Root Endpoint" "GET" "$API_GATEWAY_URL/"
test_endpoint "Info Endpoint" "GET" "$API_GATEWAY_URL/info"
test_endpoint "OpenAPI Docs" "GET" "$API_GATEWAY_URL/docs"

# Resource Scanner basic endpoints
echo ""
echo -e "${YELLOW} Resource Scanner Basic Endpoints${NC}"
test_endpoint "Scanner Root" "GET" "$RESOURCE_SCANNER_URL/"
test_endpoint "Scanner Metrics" "GET" "$RESOURCE_SCANNER_URL/metrics"

# Authentication flow
echo ""
echo -e "${YELLOW} Authentication Flow${NC}"

# Register user
register_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User\",\"company\":\"Test Company\"}"
test_endpoint "User Registration" "POST" "$API_GATEWAY_URL/auth/register" "$register_data"

# Login and get token
login_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}"
echo -n "Getting auth token... "
if token_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$API_GATEWAY_URL/auth/login"); then
    AUTH_TOKEN=$(echo "$token_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    if [ -n "$AUTH_TOKEN" ]; then
        echo -e "${GREEN}✓ SUCCESS${NC}"
    else
        echo -e "${RED}✗ FAILED${NC} (Could not extract token)"
        AUTH_TOKEN=""
    fi
else
    echo -e "${RED}✗ FAILED${NC} (Login request failed)"
    AUTH_TOKEN=""
fi

# Test authenticated endpoints if we have a token
if [ -n "$AUTH_TOKEN" ]; then
    echo ""
    echo -e "${YELLOW} Authenticated Endpoints${NC}"
    test_endpoint "Get Current User" "GET" "$API_GATEWAY_URL/auth/me" "" "$AUTH_TOKEN"
    test_endpoint "Cost Summary" "GET" "$API_GATEWAY_URL/costs/summary" "" "$AUTH_TOKEN"
    test_endpoint "Cost Details" "GET" "$API_GATEWAY_URL/costs/details?days=7" "" "$AUTH_TOKEN"
    test_endpoint "Cost Forecast" "GET" "$API_GATEWAY_URL/costs/forecast?months=3" "" "$AUTH_TOKEN"
    test_endpoint "Optimization Recommendations" "GET" "$API_GATEWAY_URL/costs/optimization" "" "$AUTH_TOKEN"
    test_endpoint "Services Health Check" "GET" "$API_GATEWAY_URL/costs/services/health" "" "$AUTH_TOKEN"
    test_endpoint "Analytics Dashboard" "GET" "$API_GATEWAY_URL/costs/analytics/dashboard" "" "$AUTH_TOKEN"
    
    # Test resource scanning
    echo ""
    echo -e "${YELLOW} Resource Scanning${NC}"
    scan_data='{"regions":["us-west-2"],"include_costs":true,"scan_types":["ec2","rds","s3"]}'
    test_endpoint "Trigger Resource Scan" "POST" "$API_GATEWAY_URL/costs/scan/trigger" "$scan_data" "$AUTH_TOKEN"
    
    ec2_scan_data='{"region":"us-west-2","include_costs":true}'
    test_endpoint "EC2 Scan" "POST" "$API_GATEWAY_URL/costs/scan/ec2" "$ec2_scan_data" "$AUTH_TOKEN"
    
    test_endpoint "Live EC2 Optimization" "GET" "$API_GATEWAY_URL/costs/optimization/live/ec2" "" "$AUTH_TOKEN"
    test_endpoint "Live RDS Optimization" "GET" "$API_GATEWAY_URL/costs/optimization/live/rds" "" "$AUTH_TOKEN"
    test_endpoint "Live S3 Optimization" "GET" "$API_GATEWAY_URL/costs/optimization/live/s3" "" "$AUTH_TOKEN"
else
    echo ""
    echo -e "${YELLOW} Skipping authenticated endpoint tests (no auth token)${NC}"
fi

# Test Resource Scanner direct endpoints
echo ""
echo -e "${YELLOW} Resource Scanner Direct Tests${NC}"
test_endpoint "EC2 Optimization Recommendations" "GET" "$RESOURCE_SCANNER_URL/optimize/ec2"
test_endpoint "RDS Optimization Recommendations" "GET
test_endpoint "RDS Optimization Recommendations" "GET" "$RESOURCE_SCANNER_URL/optimize/rds"
test_endpoint "S3 Optimization Recommendations" "GET" "$RESOURCE_SCANNER_URL/optimize/s3"

# Direct resource scanning
scan_all_data='{"regions":["us-west-2"],"include_costs":true}'
test_endpoint "Direct All Resources Scan" "POST" "$RESOURCE_SCANNER_URL/scan/all" "$scan_all_data"

ec2_direct_data='{"region":"us-west-2","include_costs":true}'
test_endpoint "Direct EC2 Scan" "POST" "$RESOURCE_SCANNER_URL/scan/ec2" "$ec2_direct_data"

rds_direct_data='{"region":"us-west-2","include_costs":true}'
test_endpoint "Direct RDS Scan" "POST" "$RESOURCE_SCANNER_URL/scan/rds" "$rds_direct_data"

s3_direct_data='{"include_costs":true}'
test_endpoint "Direct S3 Scan" "POST" "$RESOURCE_SCANNER_URL/scan/s3" "$s3_direct_data"

# Error handling tests
echo ""
echo -e "${YELLOW} Error Handling Tests${NC}"
test_endpoint "Invalid Optimization Type" "GET" "$RESOURCE_SCANNER_URL/optimize/invalid" "" "" "400"
test_endpoint "404 Endpoint" "GET" "$API_GATEWAY_URL/nonexistent" "" "" "404"
test_endpoint "Unauthorized Access" "GET" "$API_GATEWAY_URL/costs/summary" "" "" "401"

# Cleanup
rm -f /tmp/test_response

# Summary
echo ""

echo -e "${BLUE}           Test Summary                 ${NC}"
echo ""

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e " ${GREEN}All tests passed!${NC} ($PASSED_TESTS/$TOTAL_TESTS)"
    echo -e " ${GREEN}All API endpoints are working correctly!${NC}"
    exit 0
else
    FAILED_TESTS=$((TOTAL_TESTS - PASSED_TESTS))
    echo -e " ${RED}Some tests failed${NC}"
    echo -e " ${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e " ${RED}Failed: $FAILED_TESTS${NC}"
    echo -e " ${YELLOW}Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%${NC}"
    exit 1
fi