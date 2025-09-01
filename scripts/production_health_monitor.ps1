# Production Health Monitor for FISO Multi-Cloud System
# Comprehensive monitoring script for AWS, Azure, GCP, and Kubernetes deployment

param(
    [switch]$Continuous = $false,
    [int]$IntervalSeconds = 60,
    [switch]$Detailed = $false,
    [switch]$ExportMetrics = $false
)

Write-Host "🔍 FISO Production Health Monitor" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Configuration
$endpoints = @{
    "AWS Lambda" = @{
        "health" = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod/health"
        "orchestrate" = "https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod/orchestrate"
    }
    "Azure Functions" = @{
        "health" = "https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc"
    }
    "GCP Emulator" = @{
        "health" = "http://localhost:8080"
        "orchestrate" = "http://localhost:8080?action=orchestrate"
    }
}

$clusterName = "fiso-eks-cluster"
$metricsFile = "fiso_health_metrics_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

function Test-EndpointHealth {
    param($name, $url, $timeout = 10)
    
    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec $timeout -ErrorAction Stop
        $end = Get-Date
        $responseTime = ($end - $start).TotalMilliseconds
        
        return @{
            Name = $name
            URL = $url
            Status = "✅ HEALTHY"
            ResponseTime = [math]::Round($responseTime, 2)
            Timestamp = $start
            Response = $response
        }
    }
    catch {
        return @{
            Name = $name
            URL = $url
            Status = "❌ UNHEALTHY"
            ResponseTime = $null
            Timestamp = Get-Date
            Error = $_.Exception.Message
        }
    }
}

function Get-KubernetesHealth {
    try {
        # Check cluster connectivity
        $clusterInfo = kubectl cluster-info --request-timeout=10s 2>&1
        if ($LASTEXITCODE -ne 0) {
            return @{
                Status = "❌ CLUSTER UNREACHABLE"
                Nodes = 0
                Pods = 0
                Services = 0
                Error = "Cannot connect to cluster"
            }
        }

        # Get node status
        $nodes = kubectl get nodes --no-headers 2>&1
        $nodeCount = 0
        $readyNodes = 0
        if ($LASTEXITCODE -eq 0) {
            $nodeLines = $nodes | Where-Object { $_ -and $_.Trim() -ne "" }
            $nodeCount = $nodeLines.Count
            $readyNodes = ($nodeLines | Where-Object { $_ -match "\s+Ready\s+" }).Count
        }

        # Get pod status
        $pods = kubectl get pods --all-namespaces --no-headers 2>&1
        $podCount = 0
        $runningPods = 0
        if ($LASTEXITCODE -eq 0) {
            $podLines = $pods | Where-Object { $_ -and $_.Trim() -ne "" }
            $podCount = $podLines.Count
            $runningPods = ($podLines | Where-Object { $_ -match "\s+Running\s+" }).Count
        }

        # Get service status
        $services = kubectl get services --all-namespaces --no-headers 2>&1
        $serviceCount = 0
        if ($LASTEXITCODE -eq 0) {
            $serviceLines = $services | Where-Object { $_ -and $_.Trim() -ne "" }
            $serviceCount = $serviceLines.Count
        }

        $overallStatus = if ($readyNodes -gt 0 -and $runningPods -gt 0) { "✅ HEALTHY" } else { "⚠️  DEGRADED" }

        return @{
            Status = $overallStatus
            Nodes = "$readyNodes/$nodeCount"
            Pods = "$runningPods/$podCount"
            Services = $serviceCount
            Details = @{
                NodesReady = $readyNodes
                TotalNodes = $nodeCount
                PodsRunning = $runningPods
                TotalPods = $podCount
                TotalServices = $serviceCount
            }
        }
    }
    catch {
        return @{
            Status = "❌ ERROR"
            Error = $_.Exception.Message
        }
    }
}

function Get-ResourceUtilization {
    try {
        # AWS Lambda metrics (simplified)
        $awsHealth = Test-EndpointHealth "AWS Health Check" $endpoints."AWS Lambda".health
        
        # Azure Functions metrics  
        $azureHealth = Test-EndpointHealth "Azure Health Check" $endpoints."Azure Functions".health
        
        # GCP Emulator metrics
        $gcpHealth = Test-EndpointHealth "GCP Health Check" $endpoints."GCP Emulator".health
        
        # Kubernetes resource usage
        $k8sHealth = Get-KubernetesHealth
        
        return @{
            AWS = $awsHealth
            Azure = $azureHealth
            GCP = $gcpHealth
            Kubernetes = $k8sHealth
            Timestamp = Get-Date
        }
    }
    catch {
        Write-Error "Failed to get resource utilization: $($_.Exception.Message)"
        return $null
    }
}

function Show-HealthSummary {
    param($healthData)
    
    Write-Host "`n🩺 Multi-Cloud Health Summary" -ForegroundColor Yellow
    Write-Host "Time: $(Get-Date)" -ForegroundColor Gray
    Write-Host "=" * 50
    
    # Cloud Provider Status
    Write-Host "`n☁️  Cloud Providers:" -ForegroundColor Cyan
    $awsTime = if($healthData.AWS.ResponseTime) { "$($healthData.AWS.ResponseTime) ms" } else { "N/A" }
    $azureTime = if($healthData.Azure.ResponseTime) { "$($healthData.Azure.ResponseTime) ms" } else { "N/A" }
    $gcpTime = if($healthData.GCP.ResponseTime) { "$($healthData.GCP.ResponseTime) ms" } else { "N/A" }
    
    Write-Host "  AWS Lambda:      $($healthData.AWS.Status) ($awsTime)" -ForegroundColor $(if($healthData.AWS.Status -like "*HEALTHY*") { "Green" } else { "Red" })
    Write-Host "  Azure Functions: $($healthData.Azure.Status) ($azureTime)" -ForegroundColor $(if($healthData.Azure.Status -like "*HEALTHY*") { "Green" } else { "Red" })
    Write-Host "  GCP Emulator:    $($healthData.GCP.Status) ($gcpTime)" -ForegroundColor $(if($healthData.GCP.Status -like "*HEALTHY*") { "Green" } else { "Red" })
    
    # Kubernetes Status
    Write-Host "`n🎯 Kubernetes Cluster:" -ForegroundColor Cyan
    Write-Host "  Overall:         $($healthData.Kubernetes.Status)" -ForegroundColor $(if($healthData.Kubernetes.Status -like "*HEALTHY*") { "Green" } elseif($healthData.Kubernetes.Status -like "*DEGRADED*") { "Yellow" } else { "Red" })
    if ($healthData.Kubernetes.Nodes) {
        Write-Host "  Nodes Ready:     $($healthData.Kubernetes.Nodes)" -ForegroundColor Gray
        Write-Host "  Pods Running:    $($healthData.Kubernetes.Pods)" -ForegroundColor Gray
        Write-Host "  Services:        $($healthData.Kubernetes.Services)" -ForegroundColor Gray
    }
    
    if ($Detailed -and $healthData.Kubernetes.Error) {
        Write-Host "  Error: $($healthData.Kubernetes.Error)" -ForegroundColor Red
    }
}

function Test-ProductionReadiness {
    Write-Host "`n🚀 Production Readiness Assessment" -ForegroundColor Magenta
    Write-Host "=" * 40
    
    $readinessScore = 0
    $maxScore = 10
    
    # Test multi-cloud orchestration
    try {
        $orchestrateTest = Test-EndpointHealth "AWS Orchestrate" $endpoints."AWS Lambda".orchestrate
        if ($orchestrateTest.Status -like "*HEALTHY*") {
            $readinessScore += 3
            Write-Host "✅ Multi-cloud orchestration: WORKING" -ForegroundColor Green
        } else {
            Write-Host "❌ Multi-cloud orchestration: FAILED" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Multi-cloud orchestration: ERROR" -ForegroundColor Red
    }
    
    # Test individual providers
    $healthData = Get-ResourceUtilization
    $providersHealthy = 0
    
    if ($healthData.AWS.Status -like "*HEALTHY*") { $providersHealthy++; $readinessScore += 1 }
    if ($healthData.Azure.Status -like "*HEALTHY*") { $providersHealthy++; $readinessScore += 1 }
    if ($healthData.GCP.Status -like "*HEALTHY*") { $providersHealthy++; $readinessScore += 1 }
    
    Write-Host "✅ Healthy cloud providers: $providersHealthy/3" -ForegroundColor $(if($providersHealthy -eq 3) { "Green" } elseif($providersHealthy -ge 2) { "Yellow" } else { "Red" })
    
    # Test Kubernetes readiness
    if ($healthData.Kubernetes.Status -like "*HEALTHY*") {
        $readinessScore += 3
        Write-Host "✅ Kubernetes cluster: READY" -ForegroundColor Green
    } elseif ($healthData.Kubernetes.Status -like "*DEGRADED*") {
        $readinessScore += 1
        Write-Host "⚠️  Kubernetes cluster: DEGRADED" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Kubernetes cluster: NOT READY" -ForegroundColor Red
    }
    
    # Test monitoring capability
    if (Test-Path $metricsFile) {
        $readinessScore += 1
        Write-Host "✅ Monitoring and metrics: ENABLED" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Monitoring and metrics: BASIC" -ForegroundColor Yellow
    }
    
    # Calculate readiness percentage
    $readinessPercentage = [math]::Round(($readinessScore / $maxScore) * 100)
    
    Write-Host "`n📊 Production Readiness Score: $readinessScore/$maxScore ($readinessPercentage%)" -ForegroundColor $(if($readinessPercentage -ge 80) { "Green" } elseif($readinessPercentage -ge 60) { "Yellow" } else { "Red" })
    
    if ($readinessPercentage -ge 80) {
        Write-Host "🎉 SYSTEM IS PRODUCTION READY!" -ForegroundColor Green
    } elseif ($readinessPercentage -ge 60) {
        Write-Host "⚠️  SYSTEM NEEDS MINOR IMPROVEMENTS" -ForegroundColor Yellow
    } else {
        Write-Host "🔧 SYSTEM NEEDS SIGNIFICANT WORK" -ForegroundColor Red
    }
    
    return $readinessPercentage
}

function Export-HealthMetrics {
    param($healthData)
    
    if ($ExportMetrics) {
        try {
            $metricsData = @{
                Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
                MultiCloudHealth = $healthData
                SystemInfo = @{
                    Platform = $env:OS
                    PowerShellVersion = $PSVersionTable.PSVersion.ToString()
                    ComputerName = $env:COMPUTERNAME
                }
            }
            
            $json = $metricsData | ConvertTo-Json -Depth 10
            $json | Out-File -FilePath $metricsFile -Encoding UTF8
            Write-Host "📁 Metrics exported to: $metricsFile" -ForegroundColor Blue
        }
        catch {
            Write-Warning "Failed to export metrics: $($_.Exception.Message)"
        }
    }
}

# Main execution logic
do {
    Clear-Host
    Write-Host "🔍 FISO Production Health Monitor" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    
    # Get health data
    $healthData = Get-ResourceUtilization
    
    if ($healthData) {
        Show-HealthSummary $healthData
        
        if ($Detailed) {
            $readinessScore = Test-ProductionReadiness
        }
        
        Export-HealthMetrics $healthData
        
        # Show system recommendations
        Write-Host "`n💡 System Recommendations:" -ForegroundColor Blue
        if ($healthData.Kubernetes.Status -notlike "*HEALTHY*") {
            Write-Host "  • Complete Kubernetes node setup (CNI configuration)" -ForegroundColor Yellow
        }
        if ($healthData.GCP.Status -notlike "*HEALTHY*") {
            Write-Host "  • Ensure GCP emulator is running (python gcp_emulator/main.py)" -ForegroundColor Yellow
        }
        if ($healthData.AWS.ResponseTime -gt 2000) {
            Write-Host "  • AWS Lambda cold start detected - consider warming strategies" -ForegroundColor Yellow
        }
        if ($healthData.Azure.ResponseTime -gt 2000) {
            Write-Host "  • Azure Functions cold start detected - consider premium plan" -ForegroundColor Yellow
        }
    }
    
    if ($Continuous) {
        Write-Host "`n⏱️  Next check in $IntervalSeconds seconds... (Ctrl+C to stop)" -ForegroundColor Gray
        Start-Sleep -Seconds $IntervalSeconds
    }
    
} while ($Continuous)

Write-Host "`n✅ Health monitoring complete!" -ForegroundColor Green
