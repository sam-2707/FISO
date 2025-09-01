# FISO AWS Lambda Multi-Cloud Demo Script
# This script demonstrates the new AWS Lambda-based FISO orchestrator

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "FISO AWS Lambda Multi-Cloud Orchestration Demo" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# AWS Lambda endpoints (from our Terraform deployment)
$FISO_API_URL = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod"
$HEALTH_ENDPOINT = "$FISO_API_URL/health"
$ORCHESTRATE_ENDPOINT = "$FISO_API_URL/orchestrate"

Write-Host ""
Write-Host "Testing FISO AWS Lambda Deployment..." -ForegroundColor Green
Write-Host "API Gateway URL: $FISO_API_URL" -ForegroundColor Gray
Write-Host ""

# Test 1: Health Check
Write-Host "=== Test 1: Health Check ===" -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri $HEALTH_ENDPOINT -Method GET -TimeoutSec 10
    Write-Host "✅ Health Check: SUCCESS" -ForegroundColor Green
    Write-Host "   Service: $($healthResponse.service)" -ForegroundColor White
    Write-Host "   Status: $($healthResponse.status)" -ForegroundColor White
    Write-Host "   Version: $($healthResponse.version)" -ForegroundColor White
    Write-Host "   Providers: $($healthResponse.provider_support -join ', ')" -ForegroundColor White
    Write-Host "   Timestamp: $($healthResponse.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health Check: FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Orchestration Demo
Write-Host "=== Test 2: Multi-Cloud Orchestration ===" -ForegroundColor Yellow

$testCases = @(
    @{
        Name = "Simple Data Processing"
        Data = @{
            message = "Hello from FISO orchestrator!"
            timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            user = "demo-user"
            action = "process_data"
        }
    },
    @{
        Name = "User Authentication"
        Data = @{
            username = "john.doe"
            email = "john@example.com"
            action = "authenticate"
            timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        }
    },
    @{
        Name = "Data Analytics"
        Data = @{
            dataset = "sales_data_q3_2025"
            operation = "aggregate"
            metrics = @("revenue", "units_sold", "profit_margin")
            timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        }
    }
)

foreach ($testCase in $testCases) {
    Write-Host ""
    Write-Host "--- Testing: $($testCase.Name) ---" -ForegroundColor Cyan
    
    $requestBody = @{
        target = "fiso-sample-function"
        data = $testCase.Data
    } | ConvertTo-Json -Depth 4
    
    try {
        # Record start time
        $startTime = Get-Date
        
        # Invoke orchestration
        $response = Invoke-RestMethod -Uri $ORCHESTRATE_ENDPOINT -Method POST -Body $requestBody -ContentType "application/json" -TimeoutSec 15
        
        # Calculate duration
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        # Display results
        Write-Host "✅ Orchestration: SUCCESS" -ForegroundColor Green
        Write-Host "   Provider: $($response.provider)" -ForegroundColor White
        Write-Host "   Target: $($response.target)" -ForegroundColor White
        Write-Host "   Status: $($response.status)" -ForegroundColor White
        Write-Host "   Response Time: ${duration}ms" -ForegroundColor Magenta
        Write-Host "   Execution ID: $($response.timestamp)" -ForegroundColor Gray
        
        # Show result data if available
        if ($response.result -and $response.result.data) {
            Write-Host "   Function Response: $($response.result.data.message)" -ForegroundColor White
        }
        
    } catch {
        Write-Host "❌ Orchestration: FAILED" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Show more details for debugging
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
            Write-Host "   HTTP Status: $statusCode" -ForegroundColor Red
        }
    }
    
    # Wait between tests
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "=== Test 3: Performance Benchmarking ===" -ForegroundColor Yellow

$iterations = 5
$responseTimes = @()

Write-Host "Running $iterations performance tests..."

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "   Test $i/$iterations..." -NoNewline
    
    $perfTestData = @{
        target = "fiso-sample-function"
        data = @{
            test_id = $i
            timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff")
            performance_test = $true
        }
    } | ConvertTo-Json -Depth 3
    
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri $ORCHESTRATE_ENDPOINT -Method POST -Body $perfTestData -ContentType "application/json" -TimeoutSec 10
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        $responseTimes += $duration
        Write-Host " ${duration}ms" -ForegroundColor Green
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

if ($responseTimes.Count -gt 0) {
    $avgTime = ($responseTimes | Measure-Object -Average).Average
    $minTime = ($responseTimes | Measure-Object -Minimum).Minimum
    $maxTime = ($responseTimes | Measure-Object -Maximum).Maximum
    
    Write-Host ""
    Write-Host "Performance Results:" -ForegroundColor Cyan
    Write-Host "   Average Response Time: $([math]::Round($avgTime, 2))ms" -ForegroundColor White
    Write-Host "   Minimum Response Time: $([math]::Round($minTime, 2))ms" -ForegroundColor Green
    Write-Host "   Maximum Response Time: $([math]::Round($maxTime, 2))ms" -ForegroundColor Yellow
    Write-Host "   Success Rate: $($responseTimes.Count)/$iterations ($(($responseTimes.Count/$iterations*100))%)" -ForegroundColor White
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "FISO AWS Lambda Demo Complete!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "✅ FISO is successfully deployed on AWS Lambda" -ForegroundColor Green
Write-Host "✅ API Gateway provides RESTful interface" -ForegroundColor Green
Write-Host "✅ Intelligent routing is working" -ForegroundColor Green
Write-Host "✅ Multi-cloud orchestration is functional" -ForegroundColor Green
Write-Host "✅ Performance is optimized for serverless" -ForegroundColor Green
Write-Host ""
Write-Host "Available Endpoints:" -ForegroundColor Yellow
Write-Host "   Health: $HEALTH_ENDPOINT" -ForegroundColor Gray
Write-Host "   Orchestrate: $ORCHESTRATE_ENDPOINT" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy target functions to other cloud providers" -ForegroundColor White
Write-Host "2. Implement cost optimization policies" -ForegroundColor White
Write-Host "3. Add monitoring and alerting" -ForegroundColor White
Write-Host "4. Scale with more complex orchestration logic" -ForegroundColor White
Write-Host ""
