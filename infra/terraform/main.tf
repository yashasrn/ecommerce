# =============================================================================
# Root Terraform Orchestrator
# E-Commerce Cloud Infrastructure: S3 + CloudFront + ECS Fargate + RDS + ALB
# =============================================================================

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "DevOps"
  }
}

# -----------------------------------------------------------------------------
# 1. VPC & Networking Module
# -----------------------------------------------------------------------------
module "vpc" {
  source = "./modules/vpc"

  project_name              = var.project_name
  environment               = var.environment
  vpc_cidr                  = var.vpc_cidr
  availability_zones        = var.availability_zones
  public_subnet_cidrs       = var.public_subnet_cidrs
  private_app_subnet_cidrs   = var.private_app_subnet_cidrs
  private_db_subnet_cidrs    = var.private_db_subnet_cidrs
  enable_single_nat_gateway = var.enable_single_nat_gateway
  tags                      = local.common_tags
}

# -----------------------------------------------------------------------------
# 2. Security Groups Module
# -----------------------------------------------------------------------------
module "security" {
  source = "./modules/security"

  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.vpc.vpc_id
  backend_container_port = var.backend_container_port
  tags                   = local.common_tags
}

# -----------------------------------------------------------------------------
# 3. S3 Frontend Hosting Module
# -----------------------------------------------------------------------------
module "s3_frontend" {
  source = "./modules/s3_frontend"

  project_name                = var.project_name
  environment                 = var.environment
  cloudfront_distribution_arn = module.cloudfront.distribution_arn
  tags                        = local.common_tags
}

# -----------------------------------------------------------------------------
# 4. Application Load Balancer Module
# -----------------------------------------------------------------------------
module "alb" {
  source = "./modules/alb"

  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.vpc.vpc_id
  public_subnet_ids      = module.vpc.public_subnet_ids
  alb_security_group_id  = module.security.alb_security_group_id
  backend_container_port = var.backend_container_port
  health_check_path      = "/health"
  tags                   = local.common_tags
}

# -----------------------------------------------------------------------------
# 5. CloudFront CDN Module (Dual Origin: S3 Static + ALB Dynamic API)
# -----------------------------------------------------------------------------
module "cloudfront" {
  source = "./modules/cloudfront"

  project_name                   = var.project_name
  environment                    = var.environment
  s3_bucket_regional_domain_name = module.s3_frontend.bucket_regional_domain_name
  s3_bucket_id                   = module.s3_frontend.bucket_id
  alb_dns_name                   = module.alb.alb_dns_name
  tags                           = local.common_tags
}

# -----------------------------------------------------------------------------
# 6. RDS PostgreSQL 16 Database Module
# -----------------------------------------------------------------------------
module "rds" {
  source = "./modules/rds"

  project_name               = var.project_name
  environment                = var.environment
  database_name              = var.db_name
  database_username          = var.db_username
  database_subnets           = module.vpc.private_db_subnet_ids
  database_security_group_id = module.security.rds_security_group_id
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  max_allocated_storage      = var.db_max_allocated_storage
  multi_az                   = var.db_multi_az
  deletion_protection        = var.db_deletion_protection
  tags                       = local.common_tags
}

# -----------------------------------------------------------------------------
# 7. ECR Container Registry Module
# -----------------------------------------------------------------------------
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}

# -----------------------------------------------------------------------------
# 8. ECS Fargate Backend Compute Module
# -----------------------------------------------------------------------------
module "ecs" {
  source = "./modules/ecs"

  project_name                  = var.project_name
  environment                   = var.environment
  aws_region                    = var.aws_region
  private_app_subnet_ids        = module.vpc.private_app_subnet_ids
  ecs_backend_security_group_id = module.security.ecs_backend_security_group_id
  backend_target_group_arn      = module.alb.backend_target_group_arn
  backend_image                 = "${module.ecr.repository_url}:${var.backend_image_tag}"
  backend_container_port        = var.backend_container_port
  backend_cpu                   = var.backend_cpu
  backend_memory                = var.backend_memory
  desired_count                 = var.backend_desired_count
  min_capacity                  = var.backend_min_capacity
  max_capacity                  = var.backend_max_capacity
  db_secret_arn                 = module.rds.db_secret_arn
  cloudwatch_log_group_name     = module.monitoring.log_group_name
  tags                          = local.common_tags
}

# -----------------------------------------------------------------------------
# 9. Centralized Monitoring, Logging & Dashboards Module
# -----------------------------------------------------------------------------
module "monitoring" {
  source = "./modules/monitoring"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  log_retention_in_days       = var.log_retention_in_days
  ecs_cluster_name            = module.ecs.cluster_name
  ecs_service_name            = module.ecs.service_name
  alb_arn_suffix              = module.alb.alb_arn_suffix
  alb_target_group_arn_suffix = module.alb.backend_target_group_arn_suffix
  rds_instance_id             = module.rds.db_instance_id
  cloudfront_distribution_id  = module.cloudfront.distribution_id
  alarm_email                 = var.alarm_email
  tags                        = local.common_tags
}
