output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster service role"
  value       = aws_iam_role.eks_cluster_role.arn
}

output "eks_cluster_role_name" {
  description = "Name of the EKS cluster service role"
  value       = aws_iam_role.eks_cluster_role.name
}

output "eks_node_role_arn" {
  description = "ARN of the EKS node group service role"
  value       = aws_iam_role.eks_node_role.arn
}

output "eks_node_role_name" {
  description = "Name of the EKS node group service role"
  value       = aws_iam_role.eks_node_role.name
}

output "costwatch_app_role_arn" {
  description = "ARN of the CostWatch application role"
  value       = aws_iam_role.costwatch_app_role.arn
}

output "costwatch_app_role_name" {
  description = "Name of the CostWatch application role"
  value       = aws_iam_role.costwatch_app_role.name
}

output "costwatch_app_policy_arn" {
  description = "ARN of the CostWatch application policy"
  value       = aws_iam_policy.costwatch_app_policy.arn
}

output "costwatch_app_instance_profile_arn" {
  description = "ARN of the CostWatch application instance profile"
  value       = aws_iam_instance_profile.costwatch_app_profile.arn
}

output "costwatch_app_instance_profile_name" {
  description = "Name of the CostWatch application instance profile"
  value       = aws_iam_instance_profile.costwatch_app_profile.name
}