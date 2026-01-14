# Terraform S3 Backend Configuration
# Store Terraform state in S3 with DynamoDB locking for team collaboration
#
# Prerequisites:
# 1. Create S3 bucket: aws s3 mb s3://costwatch-terraform-state
# 2. Enable versioning: aws s3api put-bucket-versioning --bucket costwatch-terraform-state --versioning-configuration Status=Enabled
# 3. Create DynamoDB table: aws dynamodb create-table --table-name costwatch-terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
#
# Initialize backend:
# terraform init -backend-config=environments/<env>/backend.hcl

terraform {
  backend "s3" {
    # Backend configuration is provided via backend.hcl files in environments/
    # This allows different state files for dev/staging/prod

    # Common settings (can be overridden in backend.hcl):
    encrypt        = true
    dynamodb_table = "costwatch-terraform-locks"

    # These must be provided in backend.hcl:
    # bucket = "costwatch-terraform-state"
    # key    = "environments/<env>/terraform.tfstate"
    # region = "us-west-2"
  }
}
