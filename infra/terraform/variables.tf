# -----------------------------------------------------------------------------
# Global Input Variables
# -----------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ecommerce"
}

variable "environment" {
  description = "Deployment environment name (e.g. staging, production)"
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging", "production", "dev", "prod"], var.environment)
    error_message = "Environment must be one of: staging, production, dev, prod."
  }
}

# -----------------------------------------------------------------------------
# Network Sizing
# -----------------------------------------------------------------------------
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to deploy into"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for private application subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "CIDR blocks for private database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

variable "enable_single_nat_gateway" {
  description = "True for staging (single NAT GW for cost savings), false for production (HA NAT per AZ)"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
variable "db_name" {
  description = "PostgreSQL default database name"
  type        = string
  default     = "ecommerce"
}

variable "db_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  default     = "dbadmin"
}

variable "db_instance_class" {
  description = "RDS instance compute class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial storage in GB for RDS"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Autoscaling max storage limit in GB for RDS"
  type        = number
  default     = 100
}

variable "db_multi_az" {
  description = "Enable Multi-AZ RDS for automated standby failover"
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Enable deletion protection on RDS"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# Backend ECS Compute Configuration
# -----------------------------------------------------------------------------
variable "backend_container_port" {
  description = "Port exposed by the Flask backend container"
  type        = number
  default     = 5000
}

variable "backend_cpu" {
  description = "Fargate vCPU units for backend task (256 = 0.25 vCPU, 512 = 0.5 vCPU, 1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Fargate RAM in MB for backend task (512, 1024, 2048)"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks running"
  type        = number
  default     = 2
}

variable "backend_min_capacity" {
  description = "Minimum number of backend tasks for autoscaling"
  type        = number
  default     = 1
}

variable "backend_max_capacity" {
  description = "Maximum number of backend tasks for autoscaling"
  type        = number
  default     = 6
}

variable "backend_image_tag" {
  description = "Docker image tag to deploy (e.g. latest, sha-12345)"
  type        = string
  default     = "latest"
}

# -----------------------------------------------------------------------------
# Observability & Alerts
# -----------------------------------------------------------------------------
variable "alarm_email" {
  description = "Optional email address to receive CloudWatch alarm notifications"
  type        = string
  default     = ""
}

variable "log_retention_in_days" {
  description = "CloudWatch log group retention period in days"
  type        = number
  default     = 30
}
