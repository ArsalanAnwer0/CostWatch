terraform {
  backend "s3" {
    bucket = "costwatch-terraform-state-dev"
    key    = "dev/terraform.tfstate"
    region = "us-west-2"
  }
}

# Provider configuration
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
  
  common_tags = merge(var.common_tags, {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
  
  # Use only first 2 AZs to keep costs down
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# IAM Module - Must be created first
module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
  environment  = var.environment
  region       = var.aws_region
  tags         = local.common_tags
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr           = var.vpc_cidr
  availability_zones = local.azs
  project_name       = var.project_name
  environment        = var.environment
  enable_nat_gateway = var.enable_nat_gateway
  tags               = local.common_tags
}

# Security Groups Module
module "security" {
  source = "../../modules/security"

  vpc_id       = module.vpc.vpc_id
  vpc_cidr     = var.vpc_cidr
  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags

  depends_on = [module.vpc]
}

# EKS Module
module "eks" {
  source = "../../modules/eks"

  project_name       = var.project_name
  environment        = var.environment
  cluster_version    = var.cluster_version
  cluster_role_arn   = module.iam.eks_cluster_role_arn
  node_role_arn      = module.iam.eks_node_role_arn
  
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  
  node_group_config = {
    instance_types = var.node_instance_types
    capacity_type  = "ON_DEMAND"
    min_size      = var.min_nodes
    max_size      = var.max_nodes
    desired_size  = var.desired_nodes
    disk_size     = var.disk_size
  }
  
  enabled_cluster_log_types = ["api", "audit", "authenticator"]
  
  tags = local.common_tags

  depends_on = [module.vpc, module.iam]
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

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

# Storage Module (if needed for future use)
# module "storage" {
#   source = "../../modules/storage"
#
#   project_name = var.project_name
#   environment  = var.environment
#   tags         = local.common_tags
# }

# Monitoring Module (when we create it)
# module "monitoring" {
#   source = "../../modules/monitoring"
#
#   project_name           = var.project_name
#   environment            = var.environment
#   region                 = var.aws_region
#   log_retention_days     = var.log_retention_days
#   tags                   = local.common_tags
# }