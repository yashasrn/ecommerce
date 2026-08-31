variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for dashboard metrics"
  type        = string
}

variable "log_retention_in_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "ecs_service_name" {
  description = "Name of the backend ECS service"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (for CloudWatch metrics)"
  type        = string
}

variable "alb_target_group_arn_suffix" {
  description = "ARN suffix of the backend Target Group (for CloudWatch metrics)"
  type        = string
}

variable "rds_instance_id" {
  description = "RDS instance ID"
  type        = string
}

variable "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for CloudWatch metrics)"
  type        = string
}

variable "alarm_email" {
  description = "Email address to receive CloudWatch alarm notifications (optional)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Common tags to apply to monitoring resources"
  type        = map(string)
  default     = {}
}
