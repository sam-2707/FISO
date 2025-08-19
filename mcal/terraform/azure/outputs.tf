output "function_app_name" {
  description = "The name of the deployed Azure Function App."
  # Change the resource type here
  value       = azurerm_linux_function_app.fiso_function.name
}

output "function_app_invoke_url" {
  description = "The invocation URL of the HTTP-triggered function."
  # And change it here as well
  value       = "https://${azurerm_linux_function_app.fiso_function.default_hostname}/api/HttpTrigger1?name=FISO"
}