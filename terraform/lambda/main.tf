terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source for current AWS caller identity
data "aws_caller_identity" "current" {}

# IAM role for Lambda function
resource "aws_iam_role" "fiso_lambda_role" {
  name = "fiso-lambda-orchestrator-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda function
resource "aws_iam_policy" "fiso_lambda_policy" {
  name        = "fiso-lambda-orchestrator-policy"
  description = "Policy for FISO Lambda orchestrator"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:Connect"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "fiso_lambda_policy_attachment" {
  role       = aws_iam_role.fiso_lambda_role.name
  policy_arn = aws_iam_policy.fiso_lambda_policy.arn
}

# Create deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda"
  output_path = "${path.module}/fiso_lambda_deployment.zip"
  
  depends_on = [
    null_resource.install_dependencies
  ]
}

# Install Python dependencies
resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../../lambda
      pip install -r requirements.txt -t .
    EOT
  }
  
  triggers = {
    requirements = filemd5("${path.module}/../../lambda/requirements.txt")
  }
}

# Lambda function
resource "aws_lambda_function" "fiso_orchestrator" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "fiso-orchestrator"
  role            = aws_iam_role.fiso_lambda_role.arn
  handler         = "lambda_handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      DEFAULT_PROVIDER = var.default_provider
      COST_THRESHOLD = var.cost_threshold
      LATENCY_THRESHOLD = var.latency_threshold
      AWS_TARGET_FUNCTION = var.aws_target_function
      DATABASE_URL = var.database_url
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.fiso_lambda_policy_attachment,
    aws_cloudwatch_log_group.fiso_lambda_logs,
  ]
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "fiso_lambda_logs" {
  name              = "/aws/lambda/fiso-orchestrator"
  retention_in_days = 14
}

# API Gateway
resource "aws_api_gateway_rest_api" "fiso_api" {
  name        = "fiso-orchestrator-api"
  description = "FISO Multi-Cloud Orchestrator API"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "orchestrate" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  parent_id   = aws_api_gateway_rest_api.fiso_api.root_resource_id
  path_part   = "orchestrate"
}

resource "aws_api_gateway_method" "orchestrate_post" {
  rest_api_id   = aws_api_gateway_rest_api.fiso_api.id
  resource_id   = aws_api_gateway_resource.orchestrate.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "orchestrate_options" {
  rest_api_id   = aws_api_gateway_rest_api.fiso_api.id
  resource_id   = aws_api_gateway_resource.orchestrate.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "orchestrate_integration" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  resource_id = aws_api_gateway_resource.orchestrate.id
  http_method = aws_api_gateway_method.orchestrate_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fiso_orchestrator.invoke_arn
}

resource "aws_api_gateway_integration" "orchestrate_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  resource_id = aws_api_gateway_resource.orchestrate.id
  http_method = aws_api_gateway_method.orchestrate_options.http_method

  type = "MOCK"
  
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

resource "aws_api_gateway_method_response" "orchestrate_options_response" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  resource_id = aws_api_gateway_resource.orchestrate.id
  http_method = aws_api_gateway_method.orchestrate_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "orchestrate_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  resource_id = aws_api_gateway_resource.orchestrate.id
  http_method = aws_api_gateway_method.orchestrate_options.http_method
  status_code = aws_api_gateway_method_response.orchestrate_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fiso_orchestrator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fiso_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "fiso_deployment" {
  depends_on = [
    aws_api_gateway_integration.orchestrate_integration,
    aws_api_gateway_integration.orchestrate_options_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
}

# API Gateway stage
resource "aws_api_gateway_stage" "fiso_stage" {
  deployment_id = aws_api_gateway_deployment.fiso_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.fiso_api.id
  stage_name    = "prod"
}

# Health check endpoint
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  parent_id   = aws_api_gateway_rest_api.fiso_api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.fiso_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "health_integration" {
  rest_api_id = aws_api_gateway_rest_api.fiso_api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fiso_orchestrator.invoke_arn
}
