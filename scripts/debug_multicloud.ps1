# Quick test to debug the multi-cloud script
Write-Host "=== FISO Multi-Cloud Debug Test ===" -ForegroundColor Cyan

$AWS_LAMBDA_URL = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod"

function Test-CloudProvider {
    param(
        [string]$Name,
        [string]$Url,
        [array]$Tests
    )
    
    Write-Host "Testing $Name..." -ForegroundColor Yellow
    $results = @()
    
    foreach ($test in $Tests) {
        Write-Host "  $($test.Name)..." -ForegroundColor Gray
        
        try {
            $uri = $Url + $test.Path
            $headers = @{ "Content-Type" = "application/json" }
            
            $startTime = Get-Date
            
            if ($test.Method -eq "GET") {
                $response = Invoke-RestMethod -Uri $uri -Method GET -Headers $headers -TimeoutSec 10
            } else {
                $body = $test.Body | ConvertTo-Json -Depth 10
                $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -Headers $headers -TimeoutSec 30
            }
            
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            
            Write-Host "    SUCCESS ($([math]::Round($duration, 2))ms)" -ForegroundColor Green
            
            $result = @{
                Test = $test.Name
                Success = $true
                Duration = $duration
                Response = $response
            }
            $results += $result
            
        } catch {
            Write-Host "    FAILED: $($_.Exception.Message)" -ForegroundColor Red
            
            $result = @{
                Test = $test.Name
                Success = $false
                Duration = 0
                Error = $_.Exception.Message
            }
            $results += $result
        }
    }
    
    Write-Host "Results for $Name : $($results.Count) total" -ForegroundColor Cyan
    foreach ($result in $results) {
        Write-Host "  - $($result.Test): Success=$($result.Success), Duration=$($result.Duration)" -ForegroundColor White
    }
    
    return $results
}

$testCases = @(
    @{
        Name = "Health Check"
        Path = "/health"
        Method = "GET"
        Body = $null
    },
    @{
        Name = "Simple Test"
        Path = ""
        Method = "POST"
        Body = @{ action = "test" }
    }
)

$awsResults = Test-CloudProvider -Name "AWS Lambda" -Url $AWS_LAMBDA_URL -Tests $testCases

Write-Host ""
Write-Host "=== Analysis ===" -ForegroundColor Cyan
Write-Host "AWS Results Count: $($awsResults.Count)" -ForegroundColor White
$successCount = ($awsResults | Where-Object { $_.Success -eq $true }).Count
Write-Host "Successful tests: $successCount" -ForegroundColor Green
$failedCount = ($awsResults | Where-Object { $_.Success -eq $false }).Count  
Write-Host "Failed tests: $failedCount" -ForegroundColor Red

$successfulWithDuration = $awsResults | Where-Object { $_.Success -eq $true -and $_.Duration -ne $null -and $_.Duration -gt 0 }
Write-Host "Successful tests with duration: $($successfulWithDuration.Count)" -ForegroundColor Cyan

if ($successfulWithDuration.Count -gt 0) {
    $avgDuration = ($successfulWithDuration | Measure-Object Duration -Average).Average
    Write-Host "Average duration: $([math]::Round($avgDuration, 2))ms" -ForegroundColor Cyan
} else {
    Write-Host "No successful tests with valid duration" -ForegroundColor Yellow
}
