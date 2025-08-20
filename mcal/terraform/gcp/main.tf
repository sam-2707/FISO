terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  # --- Add this line ---
  credentials = file("gcp-credentials.json")
}

# This resource generates a new random string every time `terraform apply` is run,
# ensuring the source code object is always seen as new.
resource "random_id" "fiso_code_version" {
  byte_length = 8
}

data "archive_file" "zip_python_code" {
  type        = "zip"
  source_dir  = var.app_path
  output_path = "${path.module}/fiso_sample_app_gcp.zip"
}

resource "google_storage_bucket" "fiso_bucket" {
  name     = "${var.gcp_project_id}-fiso-bucket"
  location = var.gcp_region
  uniform_bucket_level_access = true
  # Add force_destroy to make cleanup easier
  force_destroy = true
}

resource "google_storage_bucket_object" "fiso_code_object" {
  # The name now includes the unique random ID
  name   = "source-${random_id.fiso_code_version.hex}.zip"
  bucket = google_storage_bucket.fiso_bucket.name
  source = data.archive_file.zip_python_code.output_path
}

resource "google_cloudfunctions_function" "fiso_function" {
  name        = "fiso-sample-function-gcp"
  runtime     = "python39"
  description = "FISO sample function deployed to GCP"

  source_archive_bucket = google_storage_bucket.fiso_bucket.name
  source_archive_object = google_storage_bucket_object.fiso_code_object.name

  trigger_http        = true
  entry_point         = "handler"
  https_trigger_security_level = "SECURE_OPTIONAL"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.fiso_function.project
  region         = google_cloudfunctions_function.fiso_function.region
  cloud_function = google_cloudfunctions_function.fiso_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}