# -----------------------------------------------------------------------------
# CloudWatch Logging, Metric Alarms, and 2 Complete Monitoring Dashboards
# -----------------------------------------------------------------------------

# 1. Centralized CloudWatch Log Group for ECS Backend
resource "aws_cloudwatch_log_group" "ecs_backend" {
  name              = "/ecs/${var.project_name}-${var.environment}-backend"
  retention_in_days = var.log_retention_in_days

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-backend-logs"
    }
  )
}

# 2. Metric Filter for Application Error Logging
resource "aws_cloudwatch_log_metric_filter" "backend_errors" {
  name           = "${var.project_name}-${var.environment}-backend-errors"
  pattern        = "?ERROR ?Error ?Exception ?CRITICAL ?500"
  log_group_name = aws_cloudwatch_log_group.ecs_backend.name

  metric_transformation {
    name      = "BackendErrorCount"
    namespace = "${var.project_name}/${var.environment}/Application"
    value     = "1"
  }
}

# 3. SNS Topic for Operational Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-alerts"
    }
  )
}

resource "aws_sns_topic_subscription" "email_alert" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# -----------------------------------------------------------------------------
# CloudWatch Metric Alarms
# -----------------------------------------------------------------------------

# Alarm: ECS Service High CPU Utilization (> 80%)
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when ECS Backend CPU utilization exceeds 80% for 4 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = var.tags
}

# Alarm: ECS Service High Memory Utilization (> 80%)
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-high-memory"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when ECS Backend Memory utilization exceeds 80% for 4 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = var.tags
}

# Alarm: ALB High 5XX Error Rate
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-high-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Triggered when ALB Target 5XX errors exceed 5 in a 5-minute window"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    TargetGroup  = var.alb_target_group_arn_suffix
    LoadBalancer = var.alb_arn_suffix
  }

  tags = var.tags
}

# Alarm: ALB High Target Response Time (> 2 seconds)
resource "aws_cloudwatch_metric_alarm" "alb_latency" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 120
  statistic           = "Average"
  threshold           = 2
  alarm_description   = "Triggered when ALB Target response time averages over 2 seconds"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    TargetGroup  = var.alb_target_group_arn_suffix
    LoadBalancer = var.alb_arn_suffix
  }

  tags = var.tags
}

# Alarm: RDS High CPU Utilization (> 80%)
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when RDS PostgreSQL CPU utilization exceeds 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }

  tags = var.tags
}

# Alarm: RDS Low Free Storage Space (< 5 GB)
resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 5000000000 # 5 GB in Bytes
  alarm_description   = "Triggered when RDS Free Storage Space falls below 5 GB"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }

  tags = var.tags
}

# -----------------------------------------------------------------------------
# DASHBOARD 1: Infrastructure Overview Dashboard
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_dashboard" "infrastructure" {
  dashboard_name = "${var.project_name}-${var.environment}-infrastructure-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ALB Request Count & Target Response Time"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix, { stat = "Sum", yAxis = "left" }],
            [".", "TargetResponseTime", "LoadBalancer", var.alb_arn_suffix, "TargetGroup", var.alb_target_group_arn_suffix, { stat = "Average", yAxis = "right" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ALB HTTP Response Codes (2XX, 4XX, 5XX)"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", var.alb_arn_suffix, "TargetGroup", var.alb_target_group_arn_suffix, { stat = "Sum", color = "#2ca02c" }],
            [".", "HTTPCode_Target_4XX_Count", ".", ".", ".", ".", { stat = "Sum", color = "#ff7f0e" }],
            [".", "HTTPCode_Target_5XX_Count", ".", ".", ".", ".", { stat = "Sum", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "ECS Cluster CPU & Memory Utilization"
          region = var.aws_region
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.ecs_cluster_name, { stat = "Average", color = "#1f77b4" }],
            [".", "MemoryUtilization", ".", ".", { stat = "Average", color = "#ff7f0e" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "RDS PostgreSQL: CPU, Memory & Connections"
          region = var.aws_region
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_instance_id, { stat = "Average", yAxis = "left" }],
            [".", "DatabaseConnections", ".", ".", { stat = "Average", yAxis = "right" }],
            [".", "FreeableMemory", ".", ".", { stat = "Average", yAxis = "right" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# DASHBOARD 2: Application Performance & Service Dashboard
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_dashboard" "application" {
  dashboard_name = "${var.project_name}-${var.environment}-application-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ECS Backend Service Task Count (Running vs Desired)"
          region = var.aws_region
          metrics = [
            ["ECS/ContainerInsights", "RunningTaskCount", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name, { stat = "Average", color = "#2ca02c" }],
            [".", "DesiredTaskCount", ".", ".", ".", ".", { stat = "Average", color = "#1f77b4" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Backend Application Error Logs (Metric Filter)"
          region = var.aws_region
          metrics = [
            ["${var.project_name}/${var.environment}/Application", "BackendErrorCount", { stat = "Sum", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront Global Requests & Download Volume"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "Requests", "DistributionId", var.cloudfront_distribution_id, "Region", "Global", { stat = "Sum", yAxis = "left" }],
            [".", "BytesDownloaded", ".", ".", ".", ".", { stat = "Sum", yAxis = "right" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront Global Error Rates (4XX & 5XX)"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "4xxErrorRate", "DistributionId", var.cloudfront_distribution_id, "Region", "Global", { stat = "Average", color = "#ff7f0e" }],
            [".", "5xxErrorRate", ".", ".", ".", ".", { stat = "Average", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
        }
      }
    ]
  })
}
