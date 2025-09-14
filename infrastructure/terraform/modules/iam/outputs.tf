output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster role"
  value       = aws_iam_role.eks_cluster_role.arn
}

output "eks_node_role_arn" {
  description = "ARN of the EKS node role"
  value       = aws_iam_role.eks_node_role.arn
}

output "costwatch_app_role_arn" {
  description = "ARN of the CostWatch application role"
  value       = aws_iam_role.costwatch_app_role.arn
}

output "ecr_access_role_arn" {
  description = "ARN of the ECR access role"
  value       = aws_iam_role.ecr_access_role.arn
}

output "cloudwatch_logs_role_arn" {
  description = "ARN of the CloudWatch logs role"
  value       = aws_iam_role.cloudwatch_logs_role.arn
}

output "costwatch_app_policy_arn" {
  description = "ARN of the CostWatch application policy"
  value       = aws_iam_policy.costwatch_app_policy.arn
}