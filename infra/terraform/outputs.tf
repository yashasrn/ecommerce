# =============================================================================
# Root Outputs: Access Points & CI/CD Integration Values
# =============================================================================

# -----------------------------------------------------------------------------
# Frontend & Global Edge Endpoints
# -----------------------------------------------------------------------------
output "application_url" {
  description = "Primary URL to access the E-Commerce application via CloudFront CDN"
  value       = "https://${module.cloudfront.distribution_domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID (used for CI/CD cache invalidation)"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.cloudfront.distribution_domain_name
}

output "s3_frontend_bucket" {
  description = "Name of the S3 bucket for frontend React static assets"
  value       = module.s3_frontend.bucket_id
}

# -----------------------------------------------------------------------------
# Backend API & Load Balancer
# -----------------------------------------------------------------------------
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = module.alb.alb_arn
}

# -----------------------------------------------------------------------------
# Container Registry & Compute (CI/CD Pipeline Targets)
# -----------------------------------------------------------------------------
output "ecr_repository_url" {
  description = "URL of the Amazon ECR repository for backend Docker images"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS Cluster"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Name of the Backend ECS Fargate Service"
  value       = module.ecs.service_name
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS Task Execution Role"
  value       = module.ecs.execution_role_arn
}

# -----------------------------------------------------------------------------
# Database (RDS PostgreSQL)
# -----------------------------------------------------------------------------
output "rds_endpoint" {
  description = "PostgreSQL connection endpoint (host:port)"
  value       = module.rds.db_instance_endpoint
}

output "rds_address" {
  description = "PostgreSQL connection hostname"
  value       = module.rds.db_instance_address
}

output "rds_database_name" {
  description = "Name of the default PostgreSQL database"
  value       = module.rds.db_name
}

output "rds_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  value       = module.rds.db_secret_arn
}

# -----------------------------------------------------------------------------
# Observability & Monitoring Dashboards
# -----------------------------------------------------------------------------
output "cloudwatch_infrastructure_dashboard" {
  description = "Name of the CloudWatch Infrastructure Dashboard"
  value       = module.monitoring.infrastructure_dashboard_name
}

output "cloudwatch_application_dashboard" {
  description = "Name of the CloudWatch Application Performance Dashboard"
  value       = module.monitoring.application_dashboard_name
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch Log Group for ECS Backend"
  value       = module.monitoring.log_group_name
}
