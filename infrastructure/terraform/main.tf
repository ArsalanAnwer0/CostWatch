# CostWatch Infrastructure Main Configuration 

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration will be provided via backend.hcl
#   backend "s3" {}
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data Sources
data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

# Local Values
locals {
  account_id = data.aws_caller_identity.current.account_id
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  # Use only first 2 AZs to keep costs down
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr           = var.vpc_cidr
  availability_zones = local.azs
  project_name       = var.project_name
  environment        = var.environment
  enable_nat_gateway = var.enable_nat_gateway
}

# Security Groups Module
module "security" {
  source = "./modules/security"

  vpc_id       = module.vpc.vpc_id
  project_name = var.project_name
  environment  = var.environment

  depends_on = [module.vpc]
}

# IAM Roles and Policies Module
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  region       = var.aws_region
}

# CloudWatch Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  project_name           = var.project_name
  environment            = var.environment
  region                 = var.aws_region
  log_retention_days     = var.log_retention_days
  alert_email_addresses  = var.alert_email_addresses
  cost_anomaly_email     = var.cost_anomaly_email
}