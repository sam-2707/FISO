variable "location" {
  description = "The Azure region to deploy resources in."
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  default     = "fiso-resources"
}

variable "app_path" {
  description = "Path to the application code."
  type        = string
  default     = "../../functions/sample_app"
}