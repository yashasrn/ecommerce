variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution allowed to read from this bucket"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Common tags to apply to S3 frontend resources"
  type        = map(string)
  default     = {}
}
