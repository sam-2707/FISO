# PowerShell script to get deployment URLs from all cloud providers
# Run this from the project root directory

Write-Host "=================================================="
Write-Host "FISO Multi-Cloud Deployment URLs"
Write-Host "=================================================="

Write-Host ""
Write-Host "AWS Lambda URLs:"
Write-Host "--------------------------------------------------"
Set-Location "mcal\terraform\aws"
if (Test-Path "terraform.tfstate") {
    Write-Host "Lambda ARN:"
    try {
        $arn = terraform output -raw lambda_arn
        Write-Host $arn
    } catch {
        Write-Host "No AWS ARN found"
    }
    
    Write-Host ""
    Write-Host "Lambda Invoke URL:"
    try {
        $url = terraform output -raw lambda_invoke_url
        Write-Host $url
    } catch {
        Write-Host "No AWS URL found"
    }
} else {
    Write-Host "No AWS deployment found (terraform.tfstate missing)"
}

Write-Host ""
Write-Host "Azure Function URLs:"
Write-Host "--------------------------------------------------"
Set-Location "..\azure"
if (Test-Path "terraform.tfstate") {
    Write-Host "Function App Name:"
    try {
        $name = terraform output -raw function_app_name
        Write-Host $name
    } catch {
        Write-Host "No Azure Function App name found"
    }
    
    Write-Host ""
    Write-Host "Function App Invoke URL:"
    try {
        $url = terraform output -raw function_app_invoke_url
        Write-Host $url
    } catch {
        Write-Host "No Azure URL found"
    }
} else {
    Write-Host "No Azure deployment found (terraform.tfstate missing)"
}

Write-Host ""
Write-Host "Google Cloud Function URLs:"
Write-Host "--------------------------------------------------"
Set-Location "..\gcp"
if (Test-Path "terraform.tfstate") {
    Write-Host "Function Name:"
    try {
        $name = terraform output -raw function_name
        Write-Host $name
    } catch {
        Write-Host "No GCP Function name found"
    }
    
    Write-Host ""
    Write-Host "Function Invoke URL:"
    try {
        $url = terraform output -raw function_invoke_url
        Write-Host $url
    } catch {
        Write-Host "No GCP URL found"
    }
} else {
    Write-Host "No GCP deployment found (terraform.tfstate missing)"
}

Set-Location "..\..\..\"

Write-Host ""
Write-Host "=================================================="
Write-Host "Next Steps:"
Write-Host "1. Copy the URLs above"
Write-Host "2. Update the database using scripts\update_policies_schema.sql"
Write-Host "3. Replace placeholder URLs with actual deployment URLs"
Write-Host "4. Restart the FISO API to use multi-cloud routing"
Write-Host "=================================================="
