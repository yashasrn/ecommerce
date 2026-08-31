output "log_group_name" {
  description = "The name of the CloudWatch log group for ECS backend"
  value       = aws_cloudwatch_log_group.ecs_backend.name
}

output "log_group_arn" {
  description = "The ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs_backend.arn
}

output "sns_alerts_topic_arn" {
  description = "The ARN of the SNS topic for alarms and notifications"
  value       = aws_sns_topic.alerts.arn
}

output "infrastructure_dashboard_name" {
  description = "The name of the Infrastructure CloudWatch Dashboard"
  value       = aws_cloudwatch_dashboard.infrastructure.dashboard_name
}

output "application_dashboard_name" {
  description = "The name of the Application CloudWatch Dashboard"
  value       = aws_cloudwatch_dashboard.application.dashboard_name
}
