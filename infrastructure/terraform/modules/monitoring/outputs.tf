output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_log_group_names" {
  description = "Names of the CloudWatch log groups"
  value = {
    eks_cluster      = aws_cloudwatch_log_group.eks_cluster.name
    api_gateway      = aws_cloudwatch_log_group.api_gateway.name
    resource_scanner = aws_cloudwatch_log_group.resource_scanner.name
  }
}

output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.costwatch.dashboard_name}"
}

# output "cost_anomaly_detector_arn" {
#   description = "ARN of the cost anomaly detector"
#   value       = aws_ce_anomaly_detector.cost_anomaly.arn
# }