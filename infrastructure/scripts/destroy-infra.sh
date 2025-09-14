#!/bin/bash

# CostWatch Infrastructure Deployment Script

set -e

# Configuration
ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-west-2}
PROJECT_NAME="costwatch"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}  CostWatch Infrastructure Deployment  ${NC}"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED} Invalid environment: $ENVIRONMENT${NC}"
    echo "Valid environments: dev, staging, prod"
    exit 1
fi

echo -e "${YELLOW} Deploying infrastructure for environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW} AWS Region: ${AWS_REGION}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW} Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED} Terraform not found. Please install Terraform.${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED} AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED} AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

echo -e "${GREEN} Prerequisites check passed${NC}"
echo ""

# Navigate to environment directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="${SCRIPT_DIR}/../terraform/environments/${ENVIRONMENT}"

if [ ! -d "$ENV_DIR" ]; then
    echo -e "${RED} Environment directory not found: $ENV_DIR${NC}"
    exit 1
fi

cd "$ENV_DIR"

# Initialize Terraform backend (first time setup)
echo -e "${YELLOW} Setting up
# Initialize Terraform backend (first time setup)
echo -e "${YELLOW} Setting up Terraform backend...${NC}"

# Check if S3 backend exists, create if it doesn't
BUCKET_NAME="${PROJECT_NAME}-terraform-state-${ENVIRONMENT}"
DYNAMODB_TABLE="${PROJECT_NAME}-terraform-locks-${ENVIRONMENT}"

if ! aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo -e "${YELLOW} Creating S3 backend bucket: $BUCKET_NAME${NC}"
    
    # Create S3 bucket for state
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$AWS_REGION" \
        --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null || true
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Enable encryption
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }'
    
    echo -e "${GREEN} S3 bucket created successfully${NC}"
else
    echo -e "${GREEN} S3 bucket already exists${NC}"
fi

# Check if DynamoDB table exists, create if it doesn't
if ! aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" &>/dev/null; then
    echo -e "${YELLOW} Creating DynamoDB table: $DYNAMODB_TABLE${NC}"
    
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$AWS_REGION"
    
    echo -e "${YELLOW} Waiting for DynamoDB table to be active...${NC}"
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE"
    echo -e "${GREEN} DynamoDB table created successfully${NC}"
else
    echo -e "${GREEN} DynamoDB table already exists${NC}"
fi

echo ""

# Initialize Terraform
echo -e "${YELLOW} Initializing Terraform...${NC}"
terraform init -backend-config=backend.hcl

if [ $? -ne 0 ]; then
    echo -e "${RED} Terraform initialization failed${NC}"
    exit 1
fi

echo -e "${GREEN} Terraform initialized successfully${NC}"
echo ""

# Validate Terraform configuration
echo -e "${YELLOW} Validating Terraform configuration...${NC}"
terraform validate

if [ $? -ne 0 ]; then
    echo -e "${RED} Terraform validation failed${NC}"
    exit 1
fi

echo -e "${GREEN} Terraform configuration is valid${NC}"
echo ""

# Plan deployment
echo -e "${YELLOW} Planning infrastructure changes...${NC}"
terraform plan -var-file=terraform.tfvars -out=tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED} Terraform planning failed${NC}"
    exit 1
fi

echo ""

# Confirm deployment
echo -e "${YELLOW}  Ready to deploy infrastructure. Continue? (y/N)${NC}"
read -r confirmation

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW} Deployment cancelled${NC}"
    exit 0
fi

# Apply infrastructure
echo -e "${YELLOW} Applying infrastructure changes...${NC}"
terraform apply tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED} Terraform apply failed${NC}"
    exit 1
fi

echo -e "${GREEN} Infrastructure deployed successfully${NC}"
echo ""

# Save outputs
echo -e "${YELLOW} Saving infrastructure outputs...${NC}"
terraform output -json > outputs.json

echo -e "${GREEN} Outputs saved to outputs.json${NC}"
echo ""

# Display summary
echo -e "${BLUE}         Deployment Summary             ${NC}"
echo -e "${GREEN} Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN} Region: ${AWS_REGION}${NC}"
echo -e "${GREEN} VPC ID: $(terraform output -raw vpc_id 2>/dev/null || echo 'N/A')${NC}"
echo -e "${GREEN} Database Endpoint: $(terraform output -raw rds_endpoint 2>/dev/null || echo 'N/A')${NC}"
echo ""
echo -e "${YELLOW} Next steps:${NC}"
echo "1. Update kubeconfig: aws eks update-kubeconfig --region $AWS_REGION --name ${PROJECT_NAME}-cluster-${ENVIRONMENT}"
echo "2. Deploy applications: kubectl apply -f ../../k8s/"
echo "3. Check cluster status: kubectl get nodes"
echo ""

# Cleanup
rm -f tfplan

echo -e "${GREEN} Infrastructure deployment completed successfully!${NC}"