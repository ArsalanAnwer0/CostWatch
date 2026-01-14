# Staging Environment Backend Configuration
# Usage: terraform init -backend-config=environments/staging/backend.hcl

bucket         = "costwatch-terraform-state"
key            = "environments/staging/terraform.tfstate"
region         = "us-west-2"
encrypt        = true
dynamodb_table = "costwatch-terraform-locks"
