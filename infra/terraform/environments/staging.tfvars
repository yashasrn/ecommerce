# -----------------------------------------------------------------------------
# Staging Environment Configuration (Cost Optimized)
# -----------------------------------------------------------------------------

aws_region   = "us-east-1"
project_name = "ecommerce"
environment  = "staging"

# Networking
vpc_cidr                  = "10.0.0.0/16"
availability_zones        = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs       = ["10.0.1.0/24", "10.0.2.0/24"]
private_app_subnet_cidrs   = ["10.0.11.0/24", "10.0.12.0/24"]
private_db_subnet_cidrs    = ["10.0.21.0/24", "10.0.22.0/24"]
enable_single_nat_gateway = true # Cost savings: 1 NAT GW shared across AZs

# Database (RDS PostgreSQL)
db_name                  = "ecommerce"
db_username              = "dbadmin"
db_instance_class        = "db.t4g.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 50
db_multi_az              = false
db_deletion_protection   = false

# Backend Compute (ECS Fargate)
backend_container_port = 5000
backend_cpu            = 256
backend_memory         = 512
backend_desired_count  = 1
backend_min_capacity   = 1
backend_max_capacity   = 4
backend_image_tag      = "stage"

# Observability
log_retention_in_days = 14
alarm_email           = "devops-staging@example.com"
