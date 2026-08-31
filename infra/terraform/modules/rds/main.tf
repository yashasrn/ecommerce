# -----------------------------------------------------------------------------
# RDS PostgreSQL 16 Database with AWS Secrets Manager
# -----------------------------------------------------------------------------

# 1. DB Subnet Group (Isolated Subnets)
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  description = "Subnet group for RDS PostgreSQL in isolated private subnets"
  subnet_ids  = var.database_subnets

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# 2. DB Parameter Group (Optimized PostgreSQL 16)
resource "aws_db_parameter_group" "main" {
  name        = "${var.project_name}-${var.environment}-pg16-params"
  family      = "postgres16"
  description = "Custom parameter group for PostgreSQL 16"

  parameter {
    name  = "rds.force_ssl"
    value = "0" # Allowed for container internal VPC traffic; can be switched to 1 with SSL certs
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-pg16-params"
    }
  )
}

# 3. Secure Random Password Generation
resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 4. AWS Secrets Manager Secret
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}/${var.environment}/database"
  description             = "Master credentials and connection URL for RDS PostgreSQL"
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-secret"
    }
  )
}

# 5. RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier                  = "${var.project_name}-${var.environment}-db"
  engine                      = "postgres"
  engine_version              = "16.4"
  instance_class              = var.instance_class
  allocated_storage           = var.allocated_storage
  max_allocated_storage       = var.max_allocated_storage
  storage_type                = "gp3"
  storage_encrypted           = true
  multi_az                    = var.multi_az
  publicly_accessible         = false
  auto_minor_version_upgrade  = true
  allow_major_version_upgrade = false

  db_name  = var.database_name
  username = var.database_username
  password = random_password.db_password.result
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  vpc_security_group_ids = [var.database_security_group_id]

  backup_retention_period   = var.backup_retention_period
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:30-Mon:05:30"
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-${var.environment}-db-final-snapshot" : null

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds"
    }
  )
}

# 6. Store Database Connection Details in Secrets Manager
resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    engine       = "postgres"
    host         = aws_db_instance.main.address
    port         = aws_db_instance.main.port
    username     = var.database_username
    password     = random_password.db_password.result
    database     = var.database_name
    DATABASE_URL = "postgresql://${var.database_username}:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.database_name}"
  })
}
