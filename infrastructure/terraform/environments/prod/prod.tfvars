# Production Environment Variables for CostWatch
# Usage: terraform plan -var-file=environments/prod/prod.tfvars

# Basic Configuration
aws_region   = "us-west-2"
environment  = "prod"
project_name = "costwatch"

# Network Configuration
vpc_cidr           = "10.2.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
enable_nat_gateway = true  # Required for production
enable_vpn_gateway = false

# Logging
log_retention_days = 90  # Longer retention for compliance

# Alert Configuration
alert_email_addresses = ["production-alerts@costwatch.com", "oncall@costwatch.com", "devops@costwatch.com"]
cost_anomaly_email    = "production-alerts@costwatch.com"

# Database Configuration
db_name           = "costwatch_prod"
db_username       = "costwatch_prod_user"
db_instance_class = "db.r6g.large"  # Production-ready instance with high memory
# Note: db_password MUST be provided via AWS Secrets Manager in production
# Never commit production passwords to version control

# EKS Cluster Configuration
eks_cluster_version = "1.28"
eks_node_instance_types = ["t3.large", "t3.xlarge"]  # Production-grade instances
eks_node_capacity_type = "ON_DEMAND"  # Reliability over cost

# EKS Node Group Configuration
eks_node_group_min_size     = 3  # High availability
eks_node_group_max_size     = 10  # Auto-scaling capacity
eks_node_group_desired_size = 4  # Baseline capacity
eks_node_disk_size          = 50  # Larger disk for production workloads

# EKS Logging (All log types enabled for production)
eks_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
