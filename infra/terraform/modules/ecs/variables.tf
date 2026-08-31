variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for CloudWatch logging"
  type        = string
}

variable "private_app_subnet_ids" {
  description = "List of private application subnet IDs for ECS tasks"
  type        = list(string)
}

variable "ecs_backend_security_group_id" {
  description = "Security Group ID for ECS backend tasks"
  type        = string
}

variable "backend_target_group_arn" {
  description = "ARN of the backend ALB target group"
  type        = string
}

variable "backend_image" {
  description = "Docker image URI for the backend container"
  type        = string
}

variable "backend_container_port" {
  description = "Port exposed by the backend container"
  type        = number
  default     = 5000
}

variable "backend_cpu" {
  description = "CPU units for the backend Fargate task (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Memory (in MB) for the backend Fargate task (512 = 0.5 GB)"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of backend tasks running"
  type        = number
  default     = 2
}

variable "min_capacity" {
  description = "Minimum number of tasks for auto-scaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks for auto-scaling"
  type        = number
  default     = 6
}

variable "db_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  type        = string
}

variable "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for backend container logs"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to ECS resources"
  type        = map(string)
  default     = {}
}
