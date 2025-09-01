# FISO AWS Lambda Validation Script
# Validates that all components of the AWS Lambda deployment are working correctly

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "FISO AWS Lambda Deployment Validation" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$FISO_API_URL = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod"
$testResults = @()

function Add-TestResult($testName, $success, $message, $duration = $null) {
    $result = @{
        Test = $testName
        Success = $success
        Message = $message
        Duration = $duration
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $script:testResults += $result
    
    $status = if ($success) { "✅" } else { "❌" }
    $color = if ($success) { "Green" } else { "Red" }
    
    if ($duration) {
        Write-Host "$status $testName`: $message (${duration}ms)" -ForegroundColor $color
    } else {
        Write-Host "$status $testName`: $message" -ForegroundColor $color
    }
}

Write-Host ""
Write-Host "Validating FISO AWS Lambda Infrastructure..." -ForegroundColor Yellow
Write-Host ""

# Test 1: AWS Lambda Function Existence
Write-Host "Test 1: AWS Lambda Function" -ForegroundColor Yellow
try {
    $lambdaInfo = aws lambda get-function --function-name fiso-orchestrator --query 'Configuration.{State:State,Runtime:Runtime}' --output json | ConvertFrom-Json
    if ($lambdaInfo.State -eq "Active") {
        Add-TestResult "Lambda Function" $true "Function is active (Runtime: $($lambdaInfo.Runtime))"
    } else {
        Add-TestResult "Lambda Function" $false "Function state: $($lambdaInfo.State)"
    }
} catch {
    Add-TestResult "Lambda Function" $false "Function not found or AWS CLI error"
}

# Test 2: Target Function Existence
Write-Host "Test 2: Target Function" -ForegroundColor Yellow
try {
    $targetInfo = aws lambda get-function --function-name fiso-sample-function --query 'Configuration.State' --output text
    if ($targetInfo -eq "Active") {
        Add-TestResult "Target Function" $true "fiso-sample-function is active"
    } else {
        Add-TestResult "Target Function" $false "Target function state: $targetInfo"
    }
} catch {
    Add-TestResult "Target Function" $false "Target function not found"
}

# Test 3: API Gateway Health Check
Write-Host "Test 3: API Gateway Health" -ForegroundColor Yellow
try {
    $startTime = Get-Date
    $healthResponse = Invoke-RestMethod -Uri "$FISO_API_URL/health" -Method GET -TimeoutSec 10
    $duration = ((Get-Date) - $startTime).TotalMilliseconds
    
    if ($healthResponse.status -eq "healthy") {
        Add-TestResult "API Gateway Health" $true "Service healthy, version $($healthResponse.version)" $duration
    } else {
        Add-TestResult "API Gateway Health" $false "Unexpected health status: $($healthResponse.status)" $duration
    }
} catch {
    Add-TestResult "API Gateway Health" $false "Health endpoint not responding: $($_.Exception.Message)"
}

# Test 4: Orchestration Endpoint
Write-Host "Test 4: Orchestration Functionality" -ForegroundColor Yellow
try {
    $testData = @{
        target = "fiso-sample-function"
        data = @{
            test_type = "validation"
            timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        }
    } | ConvertTo-Json -Depth 3
    
    $startTime = Get-Date
    $orchResponse = Invoke-RestMethod -Uri "$FISO_API_URL/orchestrate" -Method POST -Body $testData -ContentType "application/json" -TimeoutSec 15
    $duration = ((Get-Date) - $startTime).TotalMilliseconds
    
    if ($orchResponse.status -eq "success") {
        Add-TestResult "Orchestration" $true "Successfully routed to $($orchResponse.provider)" $duration
    } else {
        Add-TestResult "Orchestration" $false "Orchestration failed: $($orchResponse.status)" $duration
    }
} catch {
    Add-TestResult "Orchestration" $false "Orchestration endpoint error: $($_.Exception.Message)"
}

# Summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

$successCount = ($testResults | Where-Object { $_.Success -eq $true }).Count
$totalCount = $testResults.Count
$successRate = [math]::Round(($successCount / $totalCount) * 100, 1)

Write-Host ""
Write-Host "Overall Results:" -ForegroundColor Yellow
Write-Host "   Tests Passed: $successCount/$totalCount ($successRate%)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Red" })

if ($successRate -ge 80) {
    Write-Host "🎉 FISO AWS Lambda deployment is HEALTHY!" -ForegroundColor Green
} else {
    Write-Host "⚠️  FISO AWS Lambda deployment has issues." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Detailed Results:" -ForegroundColor Yellow
$testResults | ForEach-Object {
    $status = if ($_.Success) { "PASS" } else { "FAIL" }
    $color = if ($_.Success) { "Green" } else { "Red" }
    Write-Host "   [$status] $($_.Test): $($_.Message)" -ForegroundColor $color
}

Write-Host ""
Write-Host "FISO Endpoints:" -ForegroundColor Cyan
Write-Host "   Health: $FISO_API_URL/health" -ForegroundColor Gray
Write-Host "   Orchestrate: $FISO_API_URL/orchestrate" -ForegroundColor Gray
Write-Host ""
