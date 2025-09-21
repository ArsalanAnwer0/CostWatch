output "eks_additional_security_group_id" {
  description = "ID of the additional EKS security group"
  value       = aws_security_group.eks_additional.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "alb_security_group_id" {
  description = "ID of the Application Load Balancer security group"
  value       = aws_security_group.alb.id
}

output "eks_additional_security_group_arn" {
  description = "ARN of the additional EKS security group"
  value       = aws_security_group.eks_additional.arn
}

output "rds_security_group_arn" {
  description = "ARN of the RDS security group"
  value       = aws_security_group.rds.arn
}

output "alb_security_group_arn" {
  description = "ARN of the Application Load Balancer security group"
  value       = aws_security_group.alb.arn
}