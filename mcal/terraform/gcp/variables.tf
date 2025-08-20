variable "gcp_project_id" {
  description = "The GCP Project ID to deploy resources in."
  type        = string
  # IMPORTANT: Replace this default value with your actual Project ID.
  default     = "isentropic-button-hn4q7"
}

variable "gcp_region" {
  description = "The GCP region to deploy resources in."
  type        = string
  default     = "us-central1"
}

variable "app_path" {
  description = "Path to the application code."
  type        = string
  # This points to the new GCP-specific function code.
  default     = "D:\\DS LiT\\fiso\\mcal\\functions\\sample_app_gcp"
}