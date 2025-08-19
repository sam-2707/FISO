terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Zip the Python code
data "archive_file" "zip_python_code" {
  type        = "zip"
  source_dir  = var.app_path
  output_path = "${path.module}/fiso_sample_app.zip"
}

# Create an IAM policy document for the Lambda assume role
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# 2. Create an IAM role for the Lambda function
resource "aws_iam_role" "lambda_exec_role" {
  name_prefix = var.role_name_prefix
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Attach the basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3. Create the Lambda function resource (without the incorrect url_config)
resource "aws_lambda_function" "sample_app" {
  function_name    = var.function_name
  handler          = "main.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_exec_role.arn

  filename         = data.archive_file.zip_python_code.output_path
  source_code_hash = data.archive_file.zip_python_code.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.lambda_policy
  ]
}

# 4. CORRECT WAY: Create the Function URL using a separate resource
resource "aws_lambda_function_url" "sample_app_url" {
  function_name      = aws_lambda_function.sample_app.function_name
  authorization_type = "NONE"
}