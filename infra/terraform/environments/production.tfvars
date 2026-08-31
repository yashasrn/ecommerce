# -----------------------------------------------------------------------------
# Production Environment Configuration (High Availability & Fault Tolerant)
# -----------------------------------------------------------------------------

aws_region   = "us-east-1"
project_name = "ecommerce"
environment  = "production"

# Networking (Multi-AZ with Dedicated NAT per AZ for maximum resilience)
vpc_cidr                  = "10.0.0.0/16"
availability_zones        = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs       = ["10.0.1.0/24", "10.0.2.0/24"]
private_app_subnet_cidrs  = ["10.0.11.0/24", "10.0.12.0/24"]
private_db_subnet_cidrs   = ["10.0.21.0/24", "10.0.22.0/24"]
enable_single_nat_gateway = false # High Availability: 1 NAT Gateway per AZ

# Database (RDS PostgreSQL Multi-AZ with Deletion Protection & Larger Storage)
db_name                  = "ecommerce"
db_username              = "dbadmin"
db_instance_class        = "db.t4g.small"
db_allocated_storage     = 50
db_max_allocated_storage = 200
db_multi_az              = true
db_deletion_protection   = true

# Backend Compute (ECS Fargate HA)
backend_container_port = 5000
backend_cpu            = 512
backend_memory         = 1024
backend_desired_count  = 2
backend_min_capacity   = 2
backend_max_capacity   = 10
backend_image_tag      = "prod"

# Observability
log_retention_in_days = 90
alarm_email           = "devops-alerts@example.com"
