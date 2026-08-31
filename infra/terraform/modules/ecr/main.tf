# -----------------------------------------------------------------------------
# Amazon ECR Repository for Backend Container Images
# -----------------------------------------------------------------------------

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-${var.environment}-backend"
  image_tag_mutability = var.image_tag_mutability
  force_delete         = var.environment != "production"

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-backend-ecr"
    }
  )
}

# Lifecycle Policy: Expire untagged images older than 14 days, keep last 30 tagged images
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images older than 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep last 30 tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "release", "sha-", "stage", "prod", "latest"]
          countType     = "imageCount"
          countNumber   = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
