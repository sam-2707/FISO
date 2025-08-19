output "lambda_arn" {
  description = "The ARN of the deployed Lambda function."
  value       = aws_lambda_function.sample_app.arn
}

output "lambda_invoke_url" {
  description = "The invocation URL of the Lambda function."
  # This value now comes from the new resource
  value       = aws_lambda_function_url.sample_app_url.function_url
}