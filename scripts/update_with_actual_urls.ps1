#!/usr/bin/env pwsh

Write-Host "==================================================" -ForegroundColor Blue
Write-Host "FISO URL Update Script" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Blue

Write-Host "Updating database with actual deployment URLs..." -ForegroundColor Green

# Database connection
$connectionString = "Host=localhost;Port=5432;Database=fiso;Username=fiso_user;Password=fiso_password"

# Actual URLs from deployments
$awsArn = "arn:aws:lambda:us-east-1:412374076384:function:fiso_sample_app_py"
$azureUrl = "https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc"
$gcpUrl = "https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp"

# Update policies with actual URLs
$updateSql = @"
UPDATE orchestration_policies 
SET default_arn = '$awsArn',
    azure_url = '$azureUrl', 
    gcp_url = '$gcpUrl'
WHERE default_provider = 'aws';

UPDATE orchestration_policies 
SET default_arn = '$awsArn',
    azure_url = '$azureUrl',
    gcp_url = '$gcpUrl' 
WHERE default_provider = 'azure';

UPDATE orchestration_policies 
SET default_arn = '$awsArn',
    azure_url = '$azureUrl',
    gcp_url = '$gcpUrl'
WHERE default_provider = 'gcp';

SELECT name, default_provider, default_arn, azure_url, gcp_url FROM orchestration_policies;
"@

# Execute update
$env:PGPASSWORD = "fiso_password"
$updateSql | psql -h localhost -p 5432 -U fiso_user -d fiso

Write-Host ""
Write-Host "==================================================" -ForegroundColor Blue  
Write-Host "URLs updated successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Blue

Write-Host ""
Write-Host "Current URLs:" -ForegroundColor Yellow
Write-Host "AWS ARN: $awsArn" -ForegroundColor White
Write-Host "Azure URL: $azureUrl" -ForegroundColor White  
Write-Host "GCP URL: $gcpUrl" -ForegroundColor White
Write-Host ""
Write-Host "Restart the FISO API to use updated URLs:" -ForegroundColor Yellow
Write-Host "docker-compose restart fiso_api" -ForegroundColor White
