variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "function_name" {
  description = "The name of the Lambda function."
  type        = string
  default     = "fiso_sample_app_py"
}

variable "app_path" {
  description = "Path to the application code."
  type        = string
  default     = "../../functions/sample_app"
}

variable "role_name_prefix" {
  description = "The prefix for the IAM role name."
  type        = string
  default     = "fiso-lambda-exec-role-"
}