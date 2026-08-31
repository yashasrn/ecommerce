# -----------------------------------------------------------------------------
# Security Groups: Principle of Least Privilege
# ALB SG -> ECS Backend SG -> RDS PostgreSQL SG
# -----------------------------------------------------------------------------

# 1. Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Controls inbound traffic to Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description      = "Allow HTTP inbound from anywhere (CloudFront / Internet)"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "Allow HTTPS inbound from anywhere (CloudFront / Internet)"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description     = "Allow outbound traffic to ECS tasks only"
    from_port       = var.backend_container_port
    to_port         = var.backend_container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_backend.id]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-alb-sg"
    }
  )
}

# 2. ECS Backend Tasks Security Group
resource "aws_security_group" "ecs_backend" {
  name        = "${var.project_name}-${var.environment}-ecs-backend-sg"
  description = "Controls inbound traffic to ECS backend tasks"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-ecs-backend-sg"
    }
  )
}

# Standalone rule: Ingress to ECS from ALB SG
resource "aws_security_group_rule" "ecs_backend_ingress_from_alb" {
  type                     = "ingress"
  description              = "Allow inbound from ALB SG only on backend container port"
  from_port                = var.backend_container_port
  to_port                  = var.backend_container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  security_group_id        = aws_security_group.ecs_backend.id
}

# Egress: Allow outbound HTTPS (for AWS APIs, Secrets Manager, ECR, CloudWatch, SMTP)
resource "aws_security_group_rule" "ecs_backend_egress_https" {
  type              = "egress"
  description       = "Allow outbound HTTPS for AWS services and external APIs"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_backend.id
}

# Egress: Allow outbound SMTP/Email if needed (ports 587 and 465)
resource "aws_security_group_rule" "ecs_backend_egress_smtp" {
  type              = "egress"
  description       = "Allow outbound SMTP for email notifications"
  from_port         = 587
  to_port           = 587
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_backend.id
}

# Egress: Allow outbound connection to RDS on PostgreSQL port 5432
resource "aws_security_group_rule" "ecs_backend_egress_to_rds" {
  type                     = "egress"
  description              = "Allow outbound PostgreSQL connection to RDS"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.rds.id
  security_group_id        = aws_security_group.ecs_backend.id
}

# 3. RDS PostgreSQL Security Group
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Controls inbound traffic to RDS PostgreSQL database"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-sg"
    }
  )
}

# Standalone rule: Ingress to RDS strictly from ECS backend SG
resource "aws_security_group_rule" "rds_ingress_from_ecs" {
  type                     = "ingress"
  description              = "Allow PostgreSQL access strictly from ECS backend tasks"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs_backend.id
  security_group_id        = aws_security_group.rds.id
}
