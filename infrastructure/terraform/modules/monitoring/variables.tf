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

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

variable "alert_email_addresses" {
  description = "List of email addresses for alerts"
  type        = list(string)
  default     = []
}

variable "cost_anomaly_email" {
  description = "Email address for cost anomaly alerts"
  type        = string
  default     = "admin@example.com"
}