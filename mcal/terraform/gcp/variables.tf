variable "gcp_project_id" {
  description = "The GCP Project ID to deploy resources in."
  type        = string
  # IMPORTANT: Make sure this is your actual Project ID
  default     = "famous-mix-469509-s3"
}

variable "gcp_region" {
  description = "The GCP region to deploy resources in."
  type        = string
  default     = "us-central1"
}

variable "app_path" {
  description = "Path to the application code."
  type        = string
  # This is the corrected relative path.
  default     = "../../functions/sample_app_gcp"
}