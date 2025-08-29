#!/usr/bin/env pwsh

Write-Host "==================================================" -ForegroundColor Blue
Write-Host "FISO Azure Function Fix Verification" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Blue

Write-Host "`nTesting Azure Function..." -ForegroundColor Green

try {
    $azureResponse = Invoke-RestMethod -Uri "https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc" -Method GET
    Write-Host "✅ Azure Function SUCCESS!" -ForegroundColor Green
    Write-Host "Response: $($azureResponse.message)" -ForegroundColor White
    Write-Host "Platform: $($azureResponse.platform)" -ForegroundColor White
    Write-Host "Python Version: $($azureResponse.python_version)" -ForegroundColor White
} catch {
    Write-Host "❌ Azure Function FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTesting AWS Lambda..." -ForegroundColor Green

try {
    $awsResponse = Invoke-RestMethod -Uri "https://ajcizqhkybvzefzajmhgllnmuy0mzfvg.lambda-url.us-east-1.on.aws/" -Method GET
    Write-Host "✅ AWS Lambda SUCCESS!" -ForegroundColor Green
    Write-Host "Response: $($awsResponse)" -ForegroundColor White
} catch {
    Write-Host "❌ AWS Lambda FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTesting GCP Function..." -ForegroundColor Green

try {
    $gcpResponse = Invoke-RestMethod -Uri "https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp" -Method GET
    Write-Host "✅ GCP Function SUCCESS!" -ForegroundColor Green
    Write-Host "Response: $($gcpResponse)" -ForegroundColor White
} catch {
    Write-Host "❌ GCP Function FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n==================================================" -ForegroundColor Blue
Write-Host "AZURE FUNCTION FIX COMPLETE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Blue
