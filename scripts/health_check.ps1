# FISO Production Health Monitor - Simplified Version
param(
    [switch]$Detailed = $false
)

Write-Host "FISO Production Health Monitor" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Configuration
$endpoints = @{
    "AWS_Lambda_Health" = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod/health"
    "AWS_Lambda_Orchestrate" = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod/orchestrate"
    "Azure_Functions" = "https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc"
    "GCP_Emulator_Health" = "http://localhost:8080"
    "GCP_Emulator_Orchestrate" = "http://localhost:8080?action=orchestrate"
}

function Test-EndpointHealth {
    param($name, $url)
    
    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 10 -ErrorAction Stop
        $end = Get-Date
        $responseTime = [math]::Round(($end - $start).TotalMilliseconds, 2)
        
        return @{
            Name = $name
            URL = $url
            Status = "HEALTHY"
            ResponseTime = $responseTime
            Response = $response
        }
    }
    catch {
        return @{
            Name = $name
            URL = $url
            Status = "UNHEALTHY"
            Error = $_.Exception.Message
        }
    }
}

function Get-KubernetesStatus {
    try {
        $nodes = kubectl get nodes --no-headers 2>$null
        if ($LASTEXITCODE -eq 0) {
            $nodeLines = $nodes | Where-Object { $_ -and $_.Trim() -ne "" }
            $totalNodes = $nodeLines.Count
            $readyNodes = ($nodeLines | Where-Object { $_ -match "\s+Ready\s+" }).Count
            return @{
                Status = if ($readyNodes -gt 0) { "READY" } else { "NOT_READY" }
                NodesReady = $readyNodes
                TotalNodes = $totalNodes
            }
        } else {
            return @{
                Status = "UNREACHABLE"
                Error = "Cannot connect to cluster"
            }
        }
    }
    catch {
        return @{
            Status = "ERROR"
            Error = $_.Exception.Message
        }
    }
}

Write-Host "`nTesting Cloud Providers..." -ForegroundColor Yellow

# Test all endpoints
$results = @{}
foreach ($endpoint in $endpoints.GetEnumerator()) {
    Write-Host "Testing $($endpoint.Key)..." -ForegroundColor Gray
    $results[$endpoint.Key] = Test-EndpointHealth $endpoint.Key $endpoint.Value
}

# Test Kubernetes
Write-Host "Testing Kubernetes cluster..." -ForegroundColor Gray
$k8sResult = Get-KubernetesStatus

# Display results
Write-Host "`nHealth Summary:" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green

foreach ($result in $results.GetEnumerator()) {
    $status = $result.Value.Status
    $color = if ($status -eq "HEALTHY") { "Green" } else { "Red" }
    $timeInfo = if ($result.Value.ResponseTime) { " ($($result.Value.ResponseTime) ms)" } else { "" }
    Write-Host "$($result.Key): $status$timeInfo" -ForegroundColor $color
    
    if ($Detailed -and $result.Value.Error) {
        Write-Host "  Error: $($result.Value.Error)" -ForegroundColor Red
    }
}

Write-Host "`nKubernetes Status: $($k8sResult.Status)" -ForegroundColor $(if($k8sResult.Status -eq "READY") { "Green" } else { "Red" })
if ($k8sResult.NodesReady -ne $null) {
    Write-Host "Nodes Ready: $($k8sResult.NodesReady)/$($k8sResult.TotalNodes)" -ForegroundColor Gray
}

if ($Detailed) {
    Write-Host "`nProduction Readiness Assessment:" -ForegroundColor Magenta
    Write-Host "================================" -ForegroundColor Magenta
    
    $score = 0
    $maxScore = 6
    
    # Count healthy providers
    $healthyProviders = ($results.Values | Where-Object { $_.Status -eq "HEALTHY" }).Count
    $score += [math]::Min($healthyProviders, 3)
    Write-Host "Healthy Cloud Providers: $healthyProviders/3" -ForegroundColor $(if($healthyProviders -eq 3) { "Green" } elseif($healthyProviders -ge 2) { "Yellow" } else { "Red" })
    
    # Test orchestration
    $orchestrateHealthy = $results["AWS_Lambda_Orchestrate"].Status -eq "HEALTHY"
    if ($orchestrateHealthy) { $score += 1 }
    Write-Host "Multi-cloud Orchestration: $(if($orchestrateHealthy) { 'WORKING' } else { 'FAILED' })" -ForegroundColor $(if($orchestrateHealthy) { "Green" } else { "Red" })
    
    # Test Kubernetes
    $k8sHealthy = $k8sResult.Status -eq "READY"
    if ($k8sHealthy) { $score += 2 }
    Write-Host "Kubernetes Cluster: $($k8sResult.Status)" -ForegroundColor $(if($k8sHealthy) { "Green" } else { "Red" })
    
    $percentage = [math]::Round(($score / $maxScore) * 100)
    Write-Host "`nProduction Readiness Score: $score/$maxScore ($percentage%)" -ForegroundColor $(if($percentage -ge 80) { "Green" } elseif($percentage -ge 60) { "Yellow" } else { "Red" })
    
    if ($percentage -ge 80) {
        Write-Host "STATUS: PRODUCTION READY!" -ForegroundColor Green
    } elseif ($percentage -ge 60) {
        Write-Host "STATUS: NEEDS MINOR IMPROVEMENTS" -ForegroundColor Yellow
    } else {
        Write-Host "STATUS: NEEDS SIGNIFICANT WORK" -ForegroundColor Red
    }
}

Write-Host "`nHealth check complete!" -ForegroundColor Cyan
