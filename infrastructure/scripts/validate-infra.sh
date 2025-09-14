#!/bin/bash

# CostWatch Infrastructure Validation Script

set -e

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-west-2}
PROJECT_NAME="costwatch"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'


echo -e "${BLUE}  CostWatch Infrastructure Validation  ${NC}"

echo ""

# Validation functions
validate_vpc() {
    echo -n "Checking VPC... "
    if aws ec2 describe-vpcs --filters "Name=tag:Project,Values=${PROJECT_NAME}" "Name=tag:Environment,Values=${ENVIRONMENT}" --query 'Vpcs[0].VpcId' --output text | grep -q "vpc-"; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

validate_subnets() {
    echo -n "Checking subnets... "
    subnet_count=$(aws ec2 describe-subnets --filters "Name=tag:Project,Values=${PROJECT_NAME}" "Name=tag:Environment,Values=${ENVIRONMENT}" --query 'length(Subnets)' --output text)
    if [ "$subnet_count" -ge 4 ]; then
        echo -e "${GREEN}✓ PASS${NC} ($subnet_count subnets)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected ≥4, found $subnet_count)"
        return 1
    fi
}

validate_rds() {
    echo -n "Checking RDS instance... "
    if aws rds describe-db-instances --db-instance-identifier "${PROJECT_NAME}-db-${ENVIRONMENT}" --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null | grep -q "available"; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

validate_s3() {
    echo -n "Checking S3 buckets... "
    bucket_count=$(aws s3api list-buckets --query "Buckets[?contains(Name, '${PROJECT_NAME}')].Name" --output text | wc -w)
    if [ "$bucket_count" -ge 1 ]; then
        echo -e "${GREEN}✓ PASS${NC} ($bucket_count buckets)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

validate_iam_roles() {
    echo -n "Checking IAM roles... "
    role_count=$(aws iam list-roles --query "Roles[?contains(RoleName, '${PROJECT_NAME}')].RoleName" --output text | wc -w)
    if [ "$role_count" -ge 3 ]; then
        echo -e "${GREEN}✓ PASS${NC} ($role_count roles)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected ≥3, found $role_count)"
        return 1
    fi
}

validate_cloudwatch() {
    echo -n "Checking CloudWatch log groups... "
    log_group_count=$(aws logs describe-log-groups --log-group-name-prefix "/costwatch/${ENVIRONMENT}" --query 'length(logGroups)' --output text)
    if [ "$log_group_count" -ge 1 ]; then
        echo -e "${GREEN}✓ PASS${NC} ($log_group_count log groups)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

validate_sns() {
    echo -n "Checking SNS topics... "
    if aws sns list-topics --query "Topics[?contains(TopicArn, '${PROJECT_NAME}-alerts-${ENVIRONMENT}')].TopicArn" --output text | grep -q "arn:aws:sns"; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

# Run validations
echo -e "${YELLOW} Infrastructure Validation for ${ENVIRONMENT} environment${NC}"
echo ""

TOTAL_CHECKS=0
PASSED_CHECKS=0

run_check() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if $1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
}

run_check validate_vpc
run_check validate_subnets
run_check validate_rds
run_check validate_s3
run_check validate_iam_roles
run_check validate_cloudwatch
run_check validate_sns

echo ""

echo -e "${BLUE}         Validation Summary             ${NC}"


if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e " ${GREEN}All checks passed!${NC} ($PASSED_CHECKS/$TOTAL_CHECKS)"
    echo -e " ${GREEN}Infrastructure is healthy and ready!${NC}"
    exit 0
else
    FAILED_CHECKS=$((TOTAL_CHECKS - PASSED_CHECKS))
    echo -e " ${RED}Some checks failed${NC}"
    echo -e " ${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e " ${RED}Failed: $FAILED_CHECKS${NC}"
    echo ""
    echo -e "${YELLOW} Troubleshooting:${NC}"
    echo "1. Check AWS credentials and permissions"
    echo "2. Verify infrastructure was deployed: ./deploy-infra.sh $ENVIRONMENT"
    echo "3. Check Terraform state: terraform show"
    exit 1
fi