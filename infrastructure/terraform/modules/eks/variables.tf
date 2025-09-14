variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_version" {
  description = "EKS cluster version"
  type        = string
  default     = "1.28"
}

variable "cluster_role_arn" {
  description = "ARN of the EKS cluster role"
  type        = string
}

variable "node_role_arn" {
  description = "ARN of the EKS node role"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "node_group_config" {
  description = "Node group configuration"
  type = object({
    instance_types = list(string)
    capacity_type  = string
    min_size      = number
    max_size      = number
    desired_size  = number
    disk_size     = number
  })
  default = {
    instance_types = ["t3.medium"]
    capacity_type  = "ON_DEMAND"
    min_size      = 1
    max_size      = 5
    desired_size  = 2
    disk_size     = 20
  }
}

variable "enabled_cluster_log_types" {
  description = "List of cluster log types to enable"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}