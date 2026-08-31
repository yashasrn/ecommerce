variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "database_name" {
  description = "Name of the default database to create"
  type        = string
  default     = "ecommerce"
}

variable "database_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  default     = "dbadmin"
}

variable "database_subnets" {
  description = "List of isolated database subnet IDs"
  type        = list(string)
}

variable "database_security_group_id" {
  description = "Security Group ID for RDS"
  type        = string
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage limit in GB for autoscaling"
  type        = number
  default     = 100
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "Protect database from accidental deletion"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common tags to apply to RDS resources"
  type        = map(string)
  default     = {}
}
