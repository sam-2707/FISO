# PowerShell script to switch between cloud providers in FISO
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("aws", "azure", "gcp")]
    [string]$Provider
)

Write-Host "=================================================="
Write-Host "FISO Multi-Cloud Provider Switcher"
Write-Host "=================================================="

# Docker container name for PostgreSQL
$containerName = "fiso_db"

Write-Host "Switching active policy to: $Provider" -ForegroundColor Yellow

# SQL commands to switch providers
$sqlCommands = @"
-- Deactivate all policies
UPDATE policies SET is_active = false WHERE is_active = true;

-- Activate the selected provider policy
UPDATE policies SET is_active = true WHERE name = '$Provider-first';

-- Show current active policy
SELECT id, name, default_provider, is_active, created_at 
FROM policies 
WHERE is_active = true;
"@

try {
    # Execute SQL commands in the Docker container
    Write-Host "Connecting to PostgreSQL database..." -ForegroundColor Green
    $sqlCommands | docker exec -i $containerName psql -U fiso -d fiso_db
    
    Write-Host ""
    Write-Host "Successfully switched to $Provider provider!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart the FISO API if it's running" -ForegroundColor White
    Write-Host "2. Test the orchestration endpoint:" -ForegroundColor White
    Write-Host "   Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "Error switching provider: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. Docker Desktop is running" -ForegroundColor White
    Write-Host "2. FISO database container is running: docker ps" -ForegroundColor White
    Write-Host "3. Database has been initialized with the policy schema" -ForegroundColor White
}

Write-Host "=================================================="
