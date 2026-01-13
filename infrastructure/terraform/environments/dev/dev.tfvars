# Development Environment Variables for CostWatch
# Usage: terraform plan -var-file=environments/dev/dev.tfvars

# Basic Configuration
aws_region   = "us-west-2"
environment  = "dev"
project_name = "costwatch"

# Network Configuration
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b"]
enable_nat_gateway = false  # Cost saving for dev
enable_vpn_gateway = false

# Logging
log_retention_days = 7  # Shorter retention for dev

# Alert Configuration
alert_email_addresses = ["dev-team@costwatch.com"]
cost_anomaly_email    = "dev-team@costwatch.com"

# Database Configuration
db_name           = "costwatch_dev"
db_username       = "costwatch_dev_user"
db_instance_class = "db.t3.micro"  # Smallest instance for dev
# Note: db_password should be provided via environment variable or AWS Secrets Manager
# Example: export TF_VAR_db_password="your-secure-password"

# EKS Cluster Configuration
eks_cluster_version = "1.28"
eks_node_instance_types = ["t3.small"]  # Smaller instances for dev
eks_node_capacity_type = "SPOT"  # Cost savings with spot instances

# EKS Node Group Configuration
eks_node_group_min_size     = 1
eks_node_group_max_size     = 2
eks_node_group_desired_size = 1
eks_node_disk_size          = 20

# EKS Logging
eks_enabled_log_types = ["api", "audit"]  # Minimal logging for dev
