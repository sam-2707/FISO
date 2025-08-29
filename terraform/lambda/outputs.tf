output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = "${aws_api_gateway_rest_api.fiso_api.execution_arn}"
}

output "api_gateway_invoke_url" {
  description = "Invoke URL for the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.fiso_api.id}.execute-api.${var.aws_region}.amazonaws.com/prod"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.fiso_orchestrator.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.fiso_orchestrator.arn
}

output "health_check_url" {
  description = "Health check endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.fiso_api.id}.execute-api.${var.aws_region}.amazonaws.com/prod/health"
}

output "orchestrate_endpoint_url" {
  description = "Orchestrate endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.fiso_api.id}.execute-api.${var.aws_region}.amazonaws.com/prod/orchestrate"
}
