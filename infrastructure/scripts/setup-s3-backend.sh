#!/bin/bash

# CostWatch S3 Backend Setup Script
# This script creates the S3 bucket for Terraform state storage

set -e

# Configuration
PROJECT_NAME="costwatch"
ENVIRONMENT="dev"
REGION="us-west-2"
BUCKET_NAME="${PROJECT_NAME}-terraform-state-${ENVIRONMENT}"

echo " Setting up S3 backend for CostWatch Terraform state..."
echo "Bucket name: ${BUCKET_NAME}"
echo "Region: ${REGION}"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo " AWS CLI is not configured or credentials are invalid"
    echo "Please run 'aws configure' first"
    exit 1
fi

echo " AWS CLI is configured"

# Check if bucket already exists
if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
    echo " S3 bucket ${BUCKET_NAME} already exists"
else
    echo " Creating S3 bucket ${BUCKET_NAME}..."
    
    # Create the bucket
    aws s3api create-bucket \
        --bucket "${BUCKET_NAME}" \
        --region "${REGION}" \
        --create-bucket-configuration LocationConstraint="${REGION}"
    
    echo " S3 bucket created successfully"
fi

# Enable versioning on the bucket
echo " Enabling versioning on S3 bucket..."
aws s3api put-bucket-versioning \
    --bucket "${BUCKET_NAME}" \
    --versioning-configuration Status=Enabled

# Enable server-side encryption
echo " Enabling server-side encryption..."
aws s3api put-bucket-encryption \
    --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Block public access
echo "  Blocking public access..."
aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Add bucket policy for additional security
echo " Adding bucket policy..."
aws s3api put-bucket-policy \
    --bucket "${BUCKET_NAME}" \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [
            {
                \"Sid\": \"DenyInsecureConnections\",
                \"Effect\": \"Deny\",
                \"Principal\": \"*\",
                \"Action\": \"s3:*\",
                \"Resource\": [
                    \"arn:aws:s3:::${BUCKET_NAME}\",
                    \"arn:aws:s3:::${BUCKET_NAME}/*\"
                ],
                \"Condition\": {
                    \"Bool\": {
                        \"aws:SecureTransport\": \"false\"
                    }
                }
            }
        ]
    }"

echo ""
echo " S3 backend setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. cd infrastructure/terraform/environments/dev"
echo "2. terraform init"
echo "3. terraform plan"
echo "4. terraform apply"
echo ""
echo "To destroy everything later:"
echo "terraform destroy"