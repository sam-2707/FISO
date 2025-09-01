# Deploy FISO to Google Cloud Run
# Fastest serverless container deployment

Write-Host "🚀 Deploying FISO to Google Cloud Run" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Configuration
$projectId = "fiso-multicloud"
$serviceName = "fiso-cloud-run"
$region = "us-central1"
$imageUri = "412374076384.dkr.ecr.us-east-1.amazonaws.com/fiso-api:latest"

Write-Host "`n📋 Deploying to Cloud Run..." -ForegroundColor Yellow

# Deploy to Cloud Run
Write-Host "Creating Cloud Run service: $serviceName" -ForegroundColor Blue
$deployResult = gcloud run deploy $serviceName `
    --image $imageUri `
    --platform managed `
    --region $region `
    --project $projectId `
    --allow-unauthenticated `
    --port 8080 `
    --memory 2Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --set-env-vars "ENV=production,POSTGRES_HOST=fiso-postgres.cgli0siy6wfn.us-east-1.rds.amazonaws.com,POSTGRES_DB=fiso_db,POSTGRES_USER=fiso_user" `
    --format json

if ($LASTEXITCODE -eq 0) {
    $serviceInfo = $deployResult | ConvertFrom-Json
    $serviceUrl = $serviceInfo.status.url
    
    Write-Host "✅ Cloud Run service deployed!" -ForegroundColor Green
    Write-Host "URL: $serviceUrl" -ForegroundColor Cyan
    
    # Test the deployment
    Write-Host "`n🧪 Testing deployment..." -ForegroundColor Yellow
    try {
        $healthResponse = Invoke-RestMethod -Uri "$serviceUrl/health" -Method GET -TimeoutSec 30
        Write-Host "✅ Health check passed!" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`n📊 Google Cloud Run Benefits:" -ForegroundColor Green
Write-Host "✅ Deploy in 30-90 seconds" -ForegroundColor Green
Write-Host "✅ Scale to zero (pay nothing when idle)" -ForegroundColor Green
Write-Host "✅ Automatic HTTPS and custom domains" -ForegroundColor Green
Write-Host "✅ Built-in traffic splitting for A/B testing" -ForegroundColor Green
