output "function_name" {
  description = "The name of the deployed Google Cloud Function."
  value       = google_cloudfunctions_function.fiso_function.name
}

output "function_invoke_url" {
  description = "The HTTPS trigger URL for the function."
  value       = "https://${google_cloudfunctions_function.fiso_function.region}-${google_cloudfunctions_function.fiso_function.project}.cloudfunctions.net/${google_cloudfunctions_function.fiso_function.name}"
}