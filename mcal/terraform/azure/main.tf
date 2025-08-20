terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2"
    }
  }
}

provider "azurerm" {
  features {}
}

# 1. Resource Group (No changes)
resource "azurerm_resource_group" "fiso_rg" {
  name     = var.resource_group_name
  location = var.location
}

# 2. Storage Account (No changes)
resource "azurerm_storage_account" "fiso_storage" {
  name                     = "fisostorage${random_string.unique.result}"
  resource_group_name      = azurerm_resource_group.fiso_rg.name
  location                 = azurerm_resource_group.fiso_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# 3. App Service Plan (No changes)
resource "azurerm_service_plan" "fiso_plan" {
  name                = "fiso-consumption-plan"
  resource_group_name = azurerm_resource_group.fiso_rg.name
  location            = azurerm_resource_group.fiso_rg.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

# 4. Zip the Python code (No changes)
data "archive_file" "zip_python_code" {
  type        = "zip"
  source_dir  = var.app_path
  output_path = "${path.module}/fiso_sample_app_azure.zip"
}

# 5. The NEW Linux Function App resource
resource "azurerm_linux_function_app" "fiso_function" {
  name                       = "fiso-sample-function-app-${random_string.unique.result}"
  resource_group_name        = azurerm_resource_group.fiso_rg.name
  location                   = azurerm_resource_group.fiso_rg.location
  storage_account_name       = azurerm_storage_account.fiso_storage.name
  storage_account_access_key = azurerm_storage_account.fiso_storage.primary_access_key
  service_plan_id            = azurerm_service_plan.fiso_plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }
  # --- ADD THIS BLOCK ---  # These settings explicitly tell Azure how to handle the deployment.
  app_settings = {
    "ENABLE_ORYX_BUILD"          = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "WEBSITE_RUN_FROM_PACKAGE"   = "1"
  }
  # --- END ADD BLOCK ---
}

# Helper for unique names (No changes)
resource "random_string" "unique" {
  length  = 6
  special = false
  upper   = false
}