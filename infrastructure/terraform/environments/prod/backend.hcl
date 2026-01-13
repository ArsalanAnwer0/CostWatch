# Production Environment Backend Configuration
# Usage: terraform init -backend-config=environments/prod/backend.hcl

bucket         = "costwatch-terraform-state-prod"
key            = "environments/prod/terraform.tfstate"
region         = "us-west-2"
encrypt        = true
dynamodb_table = "costwatch-terraform-locks-prod"
