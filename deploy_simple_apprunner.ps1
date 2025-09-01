# Simple AWS App Runner Deployment
Write-Host "Deploying FISO to AWS App Runner..." -ForegroundColor Cyan

$serviceName = "fiso-app-runner"
$imageUri = "412374076384.dkr.ecr.us-east-1.amazonaws.com/fiso-api:latest"

# Create App Runner service using AWS CLI
Write-Host "Creating App Runner service..." -ForegroundColor Yellow

# Simple JSON configuration
$config = @"
{
  "ServiceName": "$serviceName",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "$imageUri",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {
          "ENV": "production"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "NetworkConfiguration": {
    "IngressConfiguration": {
      "IsPubliclyAccessible": true
    }
  }
}
"@

# Save config and deploy
$config | Out-File -FilePath "apprunner-simple.json" -Encoding UTF8

Write-Host "Deploying with AWS CLI..." -ForegroundColor Green
aws apprunner create-service --cli-input-json file://apprunner-simple.json --region us-east-1

if ($LASTEXITCODE -eq 0) {
    Write-Host "App Runner deployment initiated!" -ForegroundColor Green
    Write-Host "Check status at: https://console.aws.amazon.com/apprunner/" -ForegroundColor Cyan
} else {
    Write-Host "Deployment failed - check AWS credentials and permissions" -ForegroundColor Red
}

# Clean up
Remove-Item "apprunner-simple.json" -Force -ErrorAction SilentlyContinue
