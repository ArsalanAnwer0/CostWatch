# Staging Environment Variables for CostWatch
# Usage: terraform plan -var-file=environments/staging/staging.tfvars

# Basic Configuration
aws_region   = "us-west-2"
environment  = "staging"
project_name = "costwatch"

# Network Configuration
vpc_cidr           = "10.1.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
enable_nat_gateway = true  # Production-like setup
enable_vpn_gateway = false

# Logging
log_retention_days = 30

# Alert Configuration
alert_email_addresses = ["staging-alerts@costwatch.com", "devops@costwatch.com"]
cost_anomaly_email    = "staging-alerts@costwatch.com"

# Database Configuration
db_name           = "costwatch_staging"
db_username       = "costwatch_staging_user"
db_instance_class = "db.t3.small"  # Mid-size for staging
# Note: db_password should be provided via environment variable or AWS Secrets Manager
# Example: export TF_VAR_db_password="your-secure-password"

# EKS Cluster Configuration
eks_cluster_version = "1.28"
eks_node_instance_types = ["t3.medium"]
eks_node_capacity_type = "ON_DEMAND"  # More stable than spot

# EKS Node Group Configuration
eks_node_group_min_size     = 2
eks_node_group_max_size     = 4
eks_node_group_desired_size = 2
eks_node_disk_size          = 30

# EKS Logging
eks_enabled_log_types = ["api", "audit", "authenticator"]
