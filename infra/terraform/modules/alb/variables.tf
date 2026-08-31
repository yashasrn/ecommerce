variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ALB and Target Group will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB placement"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security Group ID for the ALB"
  type        = string
}

variable "backend_container_port" {
  description = "Port exposed by the backend container"
  type        = number
  default     = 5000
}

variable "health_check_path" {
  description = "Health check path on the backend container"
  type        = string
  default     = "/health"
}

variable "tags" {
  description = "Common tags to apply to ALB resources"
  type        = map(string)
  default     = {}
}
