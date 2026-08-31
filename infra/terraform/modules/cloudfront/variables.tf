variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. staging, production)"
  type        = string
}

variable "s3_bucket_regional_domain_name" {
  description = "The regional domain name of the S3 frontend bucket"
  type        = string
}

variable "s3_bucket_id" {
  description = "The ID/name of the S3 frontend bucket"
  type        = string
}

variable "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  type        = string
}

variable "api_path_patterns" {
  description = "List of path patterns to route to the ALB backend origin"
  type        = list(string)
  default = [
    "/api/*",
    "/health",
    "/signup",
    "/send-otp",
    "/verify-otp",
    "/login",
    "/send-order-email",
    "/forgot-password/*",
    "/save-order",
    "/get-orders/*",
    "/seller-signup",
    "/seller-login",
    "/add-product",
    "/seller-products",
    "/products*",
    "/products/*",
    "/seller-activity",
    "/admin/*",
    "/contact-us",
    "/update-seller-status",
    "/check-seller-status",
    "/debug/*"
  ]
}

variable "price_class" {
  description = "CloudFront price class (PriceClass_100, PriceClass_200, PriceClass_All)"
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  description = "Common tags to apply to CloudFront resources"
  type        = map(string)
  default     = {}
}
