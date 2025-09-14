# CostWatch Infrastructure Main Configuration 

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }

  # Backend configuration will be provided via backend.hcl
  # backend "s3" {}
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

# Storage Module
module "storage" {
  source = "./modules/storage"

  project_name = var.project_name
  environment  = var.environment

  tags = local.common_tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = [module.security.rds_security_group_id]
  
  project_name      = var.project_name
  environment       = var.environment
  db_instance_class = var.db_instance_class
  db_name          = var.db_name
  db_username      = var.db_username
  db_password      = var.db_password

  tags = local.common_tags

  depends_on = [module.vpc, module.security]
}

# EKS Module
module "eks" {
  source = "./modules/eks"

  project_name       = var.project_name
  environment        = var.environment
  cluster_version    = var.eks_cluster_version
  cluster_role_arn   = module.iam.eks_cluster_role_arn
  node_role_arn      = module.iam.eks_node_role_arn
  
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  
  node_group_config = {
    instance_types = var.eks_node_instance_types
    capacity_type  = var.eks_node_capacity_type
    min_size      = var.eks_node_group_min_size
    max_size      = var.eks_node_group_max_size
    desired_size  = var.eks_node_group_desired_size
    disk_size     = var.eks_node_disk_size
  }
  
  enabled_cluster_log_types = var.eks_enabled_log_types

  tags = local.common_tags

  depends_on = [module.vpc, module.iam]
}