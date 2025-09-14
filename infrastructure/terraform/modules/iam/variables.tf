variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "costwatch"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}