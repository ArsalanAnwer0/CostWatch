output "app_data_bucket_id" {
  description = "ID of the app data S3 bucket"
  value       = aws_s3_bucket.app_data.id
}

output "app_data_bucket_arn" {
  description = "ARN of the app data S3 bucket"
  value       = aws_s3_bucket.app_data.arn
}

output "logs_bucket_id" {
  description = "ID of the logs S3 bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}