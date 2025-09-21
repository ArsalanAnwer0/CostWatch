# RDS Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.rds.db_instance_port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.db_instance_name
}

# Security Group Outputs
output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = module.security.rds_security_group_id
}

output "eks_additional_security_group_id" {
  description = "Additional EKS security group ID"
  value       = module.security.eks_additional_security_group_id
}