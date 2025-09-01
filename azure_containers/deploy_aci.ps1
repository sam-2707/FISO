# Deploy FISO to Azure Container Instances
# Serverless containers - even simpler than Kubernetes!

Write-Host "🚀 Deploying FISO to Azure Container Instances" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Configuration
$resourceGroup = "fiso-container-rg"
$containerName = "fiso-aci"
$location = "eastus"
$imageUri = "412374076384.dkr.ecr.us-east-1.amazonaws.com/fiso-api:latest"

Write-Host "`n📋 Creating Azure Container Instance..." -ForegroundColor Yellow

# Create resource group
Write-Host "Creating resource group: $resourceGroup" -ForegroundColor Blue
az group create --name $resourceGroup --location $location

# Deploy container
Write-Host "Deploying container: $containerName" -ForegroundColor Blue
$deployResult = az container create `
    --resource-group $resourceGroup `
    --name $containerName `
    --image $imageUri `
    --cpu 1 `
    --memory 2 `
    --ports 8080 `
    --ip-address Public `
    --dns-name-label "fiso-aci-app" `
    --environment-variables `
        ENV=production `
        POSTGRES_HOST=fiso-postgres.cgli0siy6wfn.us-east-1.rds.amazonaws.com `
        POSTGRES_DB=fiso_db `
        POSTGRES_USER=fiso_user `
    --restart-policy Always `
    --output json

if ($LASTEXITCODE -eq 0) {
    $containerInfo = $deployResult | ConvertFrom-Json
    $fqdn = $containerInfo.ipAddress.fqdn
    $ip = $containerInfo.ipAddress.ip
    
    Write-Host "✅ Container deployed successfully!" -ForegroundColor Green
    Write-Host "FQDN: $fqdn" -ForegroundColor Cyan
    Write-Host "IP Address: $ip" -ForegroundColor Gray
    Write-Host "URL: http://$fqdn:8080" -ForegroundColor Cyan
    
    # Test the deployment
    Write-Host "`n🧪 Testing deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30  # Give container time to start
    
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://$fqdn:8080/health" -Method GET -TimeoutSec 30
        Write-Host "✅ Health check passed!" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Health check failed (container might still be starting)" -ForegroundColor Yellow
    }
}

Write-Host "`n📊 Azure Container Instances Benefits:" -ForegroundColor Green
Write-Host "✅ Deploy in 30-60 seconds" -ForegroundColor Green
Write-Host "✅ Pay per second of usage" -ForegroundColor Green
Write-Host "✅ No infrastructure management" -ForegroundColor Green
Write-Host "✅ Perfect for APIs and microservices" -ForegroundColor Green
