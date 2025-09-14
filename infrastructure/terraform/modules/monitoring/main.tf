# CloudWatch and Monitoring Infrastructure

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "eks_cluster" {
  name              = "/aws/eks/${var.project_name}-cluster-${var.environment}/cluster"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-eks-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/costwatch/${var.environment}/api-gateway"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-api-gateway-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "resource_scanner" {
  name              = "/costwatch/${var.environment}/resource-scanner"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-resource-scanner-logs"
    Environment = var.environment
  }
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-${var.environment}"

  tags = {
    Name        = "${var.project_name}-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = length(var.alert_email_addresses)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_addresses[count.index]
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project_name}-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = "${var.project_name}-cluster-${var.environment}"
  }

  tags = {
    Name        = "${var.project_name}-high-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${var.project_name}-high-memory-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors EKS cluster memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = "${var.project_name}-cluster-${var.environment}"
  }

  tags = {
    Name        = "${var.project_name}-high-memory-alarm"
    Environment = var.environment
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "costwatch" {
  dashboard_name = "${var.project_name}-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/EKS", "CPUUtilization", "ClusterName", "${var.project_name}-cluster-${var.environment}"],
            ["AWS/EKS", "MemoryUtilization", "ClusterName", "${var.project_name}-cluster-${var.environment}"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "EKS Cluster Resource Utilization"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '/aws/eks/${var.project_name}-cluster-${var.environment}/cluster' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region  = var.region
          title   = "Recent EKS Cluster Logs"
        }
      }
    ]
  })
}

# Cost Anomaly Detection
# resource "aws_ce_anomaly_detector" "cost_anomaly" {
#   name         = "${var.project_name}-cost-anomaly-${var.environment}"
#   monitor_type = "DIMENSIONAL"

#   specification = jsonencode({
#     Dimension     = "SERVICE"
#     MatchOptions  = ["EQUALS"]
#     Values        = ["Amazon Elastic Container Service for Kubernetes"]
#   })
# }

# resource "aws_ce_anomaly_subscription" "cost_anomaly_subscription" {
#   name      = "${var.project_name}-cost-anomaly-subscription-${var.environment}"
#   frequency = "DAILY"
  
#   monitor_arn_list = [
#     aws_ce_anomaly_detector.cost_anomaly.arn
#   ]
  
#   subscriber {
#     type    = "EMAIL"
#     address = var.cost_anomaly_email
#   }

#   threshold_expression {
#     and {
#       dimension {
#         key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
#         values        = ["100"]
#         match_options = ["GREATER_THAN_OR_EQUAL"]
#       }
#     }
#   }
# }