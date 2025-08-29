variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "default_provider" {
  description = "Default cloud provider for intelligent routing"
  type        = string
  default     = "aws"
}

variable "cost_threshold" {
  description = "Cost threshold for intelligent routing"
  type        = string
  default     = "0.10"
}

variable "latency_threshold" {
  description = "Latency threshold in milliseconds"
  type        = string
  default     = "5000"
}

variable "aws_target_function" {
  description = "Target AWS Lambda function name"
  type        = string
  default     = "fiso-sample-function"
}

variable "database_url" {
  description = "PostgreSQL database connection URL"
  type        = string
  default     = "postgresql://fiso_user:fiso_password_123@fiso-postgres.cgli0siy6wfn.us-east-1.rds.amazonaws.com:5432/fiso_db"
}
