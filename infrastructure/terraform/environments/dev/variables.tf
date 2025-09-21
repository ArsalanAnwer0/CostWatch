# CostWatch Terraform Variables for Dev Environment

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

# VPC Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
}

# EKS Variables
variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
}

variable "node_instance_types" {
  description = "EC2 instance types for worker nodes"
  type        = list(string)
}

variable "min_nodes" {
  description = "Minimum number of worker nodes"
  type        = number
}

variable "max_nodes" {
  description = "Maximum number of worker nodes"
  type        = number
}

variable "desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
}

variable "disk_size" {
  description = "Disk size for worker nodes"
  type        = number
}

# RDS Variables
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
}

variable "db_allocated_storage" {
  description = "RDS allocated storage"
  type        = number
}

variable "db_engine_version" {
  description = "RDS engine version"
  type        = string
}

variable "db_backup_retention_period" {
  description = "RDS backup retention period"
  type        = number
}

variable "db_backup_window" {
  description = "RDS backup window"
  type        = string
}

variable "db_maintenance_window" {
  description = "RDS maintenance window"
  type        = string
}

variable "db_deletion_protection" {
  description = "RDS deletion protection"
  type        = bool
}

variable "db_skip_final_snapshot" {
  description = "Skip final snapshot when deleting RDS"
  type        = bool
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = false
}

# Security Variables
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access resources"
  type        = list(string)
}

variable "enable_waf" {
  description = "Enable WAF"
  type        = bool
}

# Monitoring Variables
variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logs"
  type        = bool
}

variable "log_retention_days" {
  description = "CloudWatch log retention days"
  type        = number
}

# Tags
variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}