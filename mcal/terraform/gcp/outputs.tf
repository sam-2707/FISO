output "function_name" {
  description = "The name of the deployed Google Cloud Function."
  value       = google_cloudfunctions_function.fiso_function.name
}

output "function_invoke_url" {
  description = "The HTTPS trigger URL for the function."
  value       = google_cloudfunctions_function.fiso_function.https_trigger_url
}