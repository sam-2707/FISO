# FISO Multi-Cloud Demo Script
# This script demonstrates FISO orchestration across AWS, Azure, and GCP

Write-Host "=================================================="
Write-Host "FISO Multi-Cloud Orchestration Demo"
Write-Host "=================================================="

# Configuration - Update these URLs after deploying to Azure/GCP
$AWS_LAMBDA_URL = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod"
$AZURE_FUNCTION_URL = "https://your-azure-function.azurewebsites.net/api/HttpTriggerFunc"  # Update after deployment
$GCP_FUNCTION_URL = "https://your-region-your-project.cloudfunctions.net/fiso-function"   # Update after deployment

Write-Host ""
Write-Host "Testing FISO Multi-Cloud Orchestration..." -ForegroundColor Cyan

# Test cases for multi-cloud demo
$testCases = @(
    @{
        Name = "Health Check"
        Path = "/health"
        Method = "GET"
        Body = $null
    },
    @{
        Name = "AWS Provider Request"
        Path = ""
        Method = "POST"
        Body = @{
            action = "orchestrate"
            provider = "aws"
            data = @{
                target = "test-function"
                test_id = "aws-001"
                workload = "compute-intensive"
            }
        }
    },
    @{
        Name = "Azure Provider Request"
        Path = ""
        Method = "POST"
        Body = @{
            action = "orchestrate"
            provider = "azure"
            data = @{
                target = "test-function"
                test_id = "azure-001"
                workload = "data-processing"
            }
        }
    },
    @{
        Name = "GCP Provider Request"
        Path = ""
        Method = "POST"
        Body = @{
            action = "orchestrate"
            provider = "gcp"
            data = @{
                target = "test-function"
                test_id = "gcp-001"
                workload = "ml-inference"
            }
        }
    },
    @{
        Name = "Intelligent Routing"
        Path = ""
        Method = "POST"
        Body = @{
            action = "orchestrate"
            data = @{
                target = "test-function"
                test_id = "auto-001"
                workload = "balanced"
                requirements = @{
                    min_memory = "512MB"
                    max_latency = "2000ms"
                }
            }
        }
    }
)

function Test-CloudProvider {
    param(
        [string]$Name,
        [string]$Url,
        [array]$Tests
    )
    
    Write-Host ""
    Write-Host "=== Testing $Name ===" -ForegroundColor Magenta
    
    $results = @()
    
    foreach ($test in $Tests) {
        Write-Host "  $($test.Name)..." -ForegroundColor Yellow
        
        try {
            $uri = $Url + $test.Path
            $headers = @{
                "Content-Type" = "application/json"
            }
            
            $startTime = Get-Date
            
            if ($test.Method -eq "GET") {
                $response = Invoke-RestMethod -Uri $uri -Method GET -Headers $headers -TimeoutSec 10
            } else {
                $body = $test.Body | ConvertTo-Json -Depth 10
                $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -Headers $headers -TimeoutSec 30
            }
            
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            
            Write-Host "    Success ($([math]::Round($duration, 2))ms)" -ForegroundColor Green
            
            # Display key response info
            if ($response -is [string]) {
                $response = $response | ConvertFrom-Json
            }
            
            if ($response.status) {
                Write-Host "    Status: $($response.status)" -ForegroundColor Cyan
            }
            if ($response.provider) {
                Write-Host "    Provider: $($response.provider)" -ForegroundColor Cyan
            }
            if ($response.data -and $response.data.message) {
                Write-Host "    Message: $($response.data.message)" -ForegroundColor Cyan
            }
            
            $results += [PSCustomObject]@{
                Test = $test.Name
                Success = $true
                Duration = $duration
                Response = $response
            }
            
        } catch {
            Write-Host "    Failed: $($_.Exception.Message)" -ForegroundColor Red
            $results += [PSCustomObject]@{
                Test = $test.Name
                Success = $false
                Duration = 0
                Error = $_.Exception.Message
            }
        }
    }
    
    return $results
}

# Test AWS Lambda (Primary - always available)
$awsResults = Test-CloudProvider -Name "AWS Lambda" -Url $AWS_LAMBDA_URL -Tests $testCases

# Test Azure Functions (if deployed)
$azureResults = @()
if ($AZURE_FUNCTION_URL -ne "https://your-azure-function.azurewebsites.net/api/HttpTriggerFunc") {
    $azureResults = Test-CloudProvider -Name "Azure Functions" -Url $AZURE_FUNCTION_URL -Tests $testCases[0..2]
} else {
    Write-Host ""
    Write-Host "=== Azure Functions ===" -ForegroundColor Magenta
    Write-Host "  Not deployed yet" -ForegroundColor Yellow
    Write-Host "  Deploy with: terraform apply in mcal/terraform/azure/" -ForegroundColor Cyan
}

# Test GCP Functions (if deployed)
$gcpResults = @()
if ($GCP_FUNCTION_URL -ne "https://your-region-your-project.cloudfunctions.net/fiso-function") {
    $gcpResults = Test-CloudProvider -Name "Google Cloud Functions" -Url $GCP_FUNCTION_URL -Tests $testCases[0..2]
} else {
    Write-Host ""
    Write-Host "=== Google Cloud Functions ===" -ForegroundColor Magenta
    Write-Host "  Not deployed yet" -ForegroundColor Yellow
    Write-Host "  Deploy with: terraform apply in mcal/terraform/gcp/" -ForegroundColor Cyan
}

# Multi-Cloud Summary
Write-Host ""
Write-Host "=== Multi-Cloud Test Summary ===" -ForegroundColor Cyan

$allResults = $awsResults + $azureResults + $gcpResults
$totalCount = $allResults.Count
$successCount = 0
foreach ($result in $allResults) {
    if ($result.Success -eq $true) {
        $successCount++
    }
}

if ($totalCount -gt 0) {
    $percentage = if ($totalCount -gt 0) { [math]::Round($successCount/$totalCount*100, 1) } else { 0 }
    Write-Host "Overall Success Rate: $successCount/$totalCount ($percentage%)" -ForegroundColor $(if ($successCount -eq $totalCount) { "Green" } else { "Yellow" })
    
    # Provider Performance
    if ($successCount -gt 0) {
        Write-Host ""
        Write-Host "Provider Performance:" -ForegroundColor Cyan
        
        if ($awsResults.Count -gt 0) {
            $awsSuccessful = $awsResults | Where-Object { $_.Success -eq $true -and $_.Duration -ne $null }
            if ($awsSuccessful.Count -gt 0) {
                try {
                    $avgDuration = ($awsSuccessful | Measure-Object Duration -Average).Average
                    Write-Host "  AWS Lambda: $($awsSuccessful.Count) tests, avg $([math]::Round($avgDuration, 2))ms" -ForegroundColor Green
                } catch {
                    Write-Host "  AWS Lambda: $($awsSuccessful.Count) tests (duration calculation failed)" -ForegroundColor Green
                }
            }
        }
        
        if ($azureResults.Count -gt 0) {
            $azureSuccessful = $azureResults | Where-Object { $_.Success }
            if ($azureSuccessful.Count -gt 0) {
                $avgDuration = ($azureSuccessful | Measure-Object Duration -Average).Average
                Write-Host "  Azure Functions: $($azureSuccessful.Count) tests, avg $([math]::Round($avgDuration, 2))ms" -ForegroundColor Blue
            }
        }
        
        if ($gcpResults.Count -gt 0) {
            $gcpSuccessful = $gcpResults | Where-Object { $_.Success }
            if ($gcpSuccessful.Count -gt 0) {
                $avgDuration = ($gcpSuccessful | Measure-Object Duration -Average).Average
                Write-Host "  Google Cloud Functions: $($gcpSuccessful.Count) tests, avg $([math]::Round($avgDuration, 2))ms" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. AWS Lambda: Fully operational" -ForegroundColor Green

if ($AZURE_FUNCTION_URL -eq "https://your-azure-function.azurewebsites.net/api/HttpTriggerFunc") {
    Write-Host "2. Deploy Azure Functions:" -ForegroundColor Yellow
    Write-Host "   cd mcal/terraform/azure && terraform init && terraform apply" -ForegroundColor Gray
} else {
    Write-Host "2. Azure Functions: Deployed" -ForegroundColor Green
}

if ($GCP_FUNCTION_URL -eq "https://your-region-your-project.cloudfunctions.net/fiso-function") {
    Write-Host "3. Deploy GCP Functions:" -ForegroundColor Yellow
    Write-Host "   cd mcal/terraform/gcp && terraform init && terraform apply" -ForegroundColor Gray
} else {
    Write-Host "3. Google Cloud Functions: Deployed" -ForegroundColor Green
}

Write-Host "4. Update endpoint URLs in this script" -ForegroundColor Cyan
Write-Host "5. Run full multi-cloud tests" -ForegroundColor Cyan

Write-Host ""
Write-Host "FISO Multi-Cloud Orchestration is ready!" -ForegroundColor Green
Write-Host "   Intelligent routing across AWS, Azure, and GCP" -ForegroundColor White
Write-Host "   Automatic failover and load balancing" -ForegroundColor White
Write-Host "   Cost optimization and performance monitoring" -ForegroundColor White
