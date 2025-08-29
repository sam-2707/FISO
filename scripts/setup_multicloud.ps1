# FISO Multi-Cloud Setup and Test Script
# This script sets up the database, updates the Go API, and tests all cloud providers

Write-Host "=================================================="
Write-Host "FISO Multi-Cloud Orchestrator Setup"
Write-Host "=================================================="

# Step 1: Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker Desktop is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and run this script again" -ForegroundColor Yellow
    exit 1
}

# Step 2: Start FISO containers
Write-Host ""
Write-Host "Starting FISO containers..." -ForegroundColor Yellow
docker-compose up -d

Start-Sleep -Seconds 10

# Step 3: Update database schema
Write-Host ""
Write-Host "Updating database schema..." -ForegroundColor Yellow
Get-Content "scripts\update_with_actual_urls.sql" | docker exec -i fiso_db psql -U fiso -d fiso_db

# Step 4: Rebuild Go API with multi-cloud support
Write-Host ""
Write-Host "Rebuilding Go API with multi-cloud support..." -ForegroundColor Yellow
docker-compose restart api

Start-Sleep -Seconds 5

# Step 5: Test the API
Write-Host ""
Write-Host "Testing multi-cloud orchestration..." -ForegroundColor Yellow

$providers = @("aws", "azure", "gcp")

foreach ($provider in $providers) {
    Write-Host ""
    Write-Host "Testing $provider provider..." -ForegroundColor Cyan
    
    # Switch to provider
    .\scripts\switch_provider.ps1 $provider
    
    Start-Sleep -Seconds 2
    
    # Test the endpoint
    try {
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8080/api/v1/orchestrate" -TimeoutSec 30
        Write-Host "Success - $provider Response:" -ForegroundColor Green
        Write-Host "   Platform: $($response.platform)" -ForegroundColor White
        Write-Host "   Provider: $($response.provider)" -ForegroundColor White
        Write-Host "   Message: $($response.message)" -ForegroundColor White
    } catch {
        Write-Host "ERROR - $provider test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=================================================="
Write-Host "Multi-Cloud Setup Complete!"
Write-Host "=================================================="
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "Switch providers: .\scripts\switch_provider.ps1 [aws|azure|gcp]" -ForegroundColor White
Write-Host "Test endpoint: Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate" -ForegroundColor White
Write-Host "View logs: docker-compose logs api" -ForegroundColor White
Write-Host "Stop containers: docker-compose down" -ForegroundColor White
