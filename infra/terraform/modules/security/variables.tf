variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "backend_container_port" {
  description = "Port exposed by the backend container"
  type        = number
  default     = 5000
}

variable "tags" {
  description = "Common tags to apply to security group resources"
  type        = map(string)
  default     = {}
}
