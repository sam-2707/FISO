# FISO Multi-Cloud Demo Script
# This script demonstrates switching between cloud providers and invoking functions

Write-Host "=================================================="
Write-Host "FISO Multi-Cloud Orchestration Demo"
Write-Host "=================================================="

$providers = @(
    @{Name="AWS"; Color="Green"; Description="Amazon Web Services Lambda"},
    @{Name="Azure"; Color="Blue"; Description="Microsoft Azure Functions"}, 
    @{Name="GCP"; Color="Yellow"; Description="Google Cloud Functions"}
)

Write-Host ""
Write-Host "This demo will:" -ForegroundColor Cyan
Write-Host "1. Switch between cloud providers" -ForegroundColor White
Write-Host "2. Invoke the same function on different clouds" -ForegroundColor White
Write-Host "3. Show cost and performance differences" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to start the demo"

foreach ($provider in $providers) {
    $providerName = $provider.Name.ToLower()
    $color = $provider.Color
    $description = $provider.Description
    
    Write-Host ""
    Write-Host ("=" * 50)
    Write-Host "Switching to $($provider.Name) ($description)" -ForegroundColor $color
    Write-Host ("=" * 50)
    
    # Switch provider
    try {
        & ".\scripts\switch_provider.ps1" $providerName | Out-Null
        
        Write-Host ""
        Write-Host "Invoking function on $($provider.Name)..." -ForegroundColor $color
        
        # Record start time
        $startTime = Get-Date
        
        # Invoke function
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8080/api/v1/orchestrate" -TimeoutSec 30
        
        # Calculate duration
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        # Display results
        Write-Host ""
        Write-Host "SUCCESS! Response from $($provider.Name):" -ForegroundColor Green
        Write-Host "   Platform: $($response.platform)" -ForegroundColor $color
        Write-Host "   Provider: $($response.provider)" -ForegroundColor $color  
        Write-Host "   Message: $($response.message)" -ForegroundColor White
        Write-Host "   Python Version: $($response.python_version)" -ForegroundColor White
        Write-Host "   Response Time: ${duration}ms" -ForegroundColor Magenta
        Write-Host "   Status Code: $($response.status_code)" -ForegroundColor White
        
    } catch {
        Write-Host "FAILED to invoke $($provider.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($providerName -ne "gcp") {
        Write-Host ""
        Write-Host "Waiting 3 seconds before next provider..." -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

Write-Host ""
Write-Host ("=" * 60)
Write-Host "Multi-Cloud Demo Complete!" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "You now have a working multi-cloud orchestrator" -ForegroundColor White
Write-Host "Functions are deployed on AWS, Azure, and GCP" -ForegroundColor White
Write-Host "Policy-driven routing allows switching between providers" -ForegroundColor White
Write-Host "Response times and costs can be compared across clouds" -ForegroundColor White
Write-Host ""
Write-Host "To switch providers anytime:" -ForegroundColor Yellow
Write-Host "   .\scripts\switch_provider.ps1 [aws|azure|gcp]" -ForegroundColor Gray
Write-Host ""
Write-Host "To test manually:" -ForegroundColor Yellow
Write-Host "   Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate" -ForegroundColor Gray
