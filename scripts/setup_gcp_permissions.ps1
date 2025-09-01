# GCP Service Account Permissions Setup
# This script grants the necessary permissions to the FISO Terraform service account

Write-Host "=== Setting up GCP Service Account Permissions ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "famous-mix-469509-s3"
$SERVICE_ACCOUNT = "fiso-terraform-admin@famous-mix-469509-s3.iam.gserviceaccount.com"

Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Service Account: $SERVICE_ACCOUNT" -ForegroundColor Yellow
Write-Host ""

# Check if gcloud is installed and authenticated
Write-Host "Checking gcloud setup..." -ForegroundColor Cyan
try {
    $currentProject = gcloud config get-value project 2>$null
    Write-Host "Current gcloud project: $currentProject" -ForegroundColor Green
    
    if ($currentProject -ne $PROJECT_ID) {
        Write-Host "Setting gcloud project to $PROJECT_ID..." -ForegroundColor Yellow
        gcloud config set project $PROJECT_ID
    }
} catch {
    Write-Host "Error: gcloud CLI not found or not authenticated" -ForegroundColor Red
    Write-Host "Please install gcloud CLI and run 'gcloud auth login'" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Granting required permissions to service account..." -ForegroundColor Cyan

# List of required roles for FISO deployment
$requiredRoles = @(
    "roles/storage.admin",           # For Cloud Storage buckets and objects
    "roles/cloudfunctions.admin",    # For Cloud Functions
    "roles/iam.serviceAccountUser",  # For service account usage
    "roles/cloudbuild.builds.builder", # For Cloud Build (if needed)
    "roles/logging.admin",           # For logging
    "roles/monitoring.admin"         # For monitoring
)

foreach ($role in $requiredRoles) {
    Write-Host "  Granting $role..." -ForegroundColor Yellow
    try {
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$SERVICE_ACCOUNT" `
            --role="$role" `
            --quiet
        Write-Host "    ✅ Success" -ForegroundColor Green
    } catch {
        Write-Host "    ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Enabling required APIs..." -ForegroundColor Cyan

$requiredAPIs = @(
    "cloudfunctions.googleapis.com",
    "storage.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
)

foreach ($api in $requiredAPIs) {
    Write-Host "  Enabling $api..." -ForegroundColor Yellow
    try {
        gcloud services enable $api --quiet
        Write-Host "    ✅ Enabled" -ForegroundColor Green
    } catch {
        Write-Host "    ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Verifying service account permissions..." -ForegroundColor Cyan
try {
    $bindings = gcloud projects get-iam-policy $PROJECT_ID --format="json" | ConvertFrom-Json
    $serviceAccountBindings = $bindings.bindings | Where-Object { $_.members -contains "serviceAccount:$SERVICE_ACCOUNT" }
    
    Write-Host "Current roles for $SERVICE_ACCOUNT :" -ForegroundColor Green
    foreach ($binding in $serviceAccountBindings) {
        Write-Host "  - $($binding.role)" -ForegroundColor White
    }
} catch {
    Write-Host "Could not verify permissions: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'terraform plan' to verify the configuration" -ForegroundColor White
Write-Host "2. Run 'terraform apply' to deploy FISO to GCP" -ForegroundColor White
Write-Host ""
Write-Host "If you still get permission errors, you may need to:" -ForegroundColor Yellow
Write-Host "- Check that the service account key file is valid" -ForegroundColor Gray
Write-Host "- Ensure you have Owner or Editor permissions on the project" -ForegroundColor Gray
Write-Host "- Wait a few minutes for permission changes to propagate" -ForegroundColor Gray
