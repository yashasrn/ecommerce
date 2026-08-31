output "alb_security_group_id" {
  description = "The ID of the ALB Security Group"
  value       = aws_security_group.alb.id
}

output "ecs_backend_security_group_id" {
  description = "The ID of the ECS Backend Tasks Security Group"
  value       = aws_security_group.ecs_backend.id
}

output "rds_security_group_id" {
  description = "The ID of the RDS Security Group"
  value       = aws_security_group.rds.id
}
