# FISO AWS Infrastructure Monitoring Script
# Monitors the status of EKS cluster and RDS database creation

param(
    [Parameter()]
    [string]$Region = "us-east-1",
    [Parameter()]
    [int]$CheckInterval = 30
)

function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Status { param($Message) Write-Host "[STATUS] $Message" -ForegroundColor Cyan }

function Get-EKSStatus {
    try {
        $status = aws eks describe-cluster --name fiso-eks-cluster --region $Region --query 'cluster.status' --output text 2>$null
        return $status
    }
    catch {
        return "NOT_FOUND"
    }
}

function Get-RDSStatus {
    try {
        $status = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region --query 'DBInstances[0].DBInstanceStatus' --output text 2>$null
        return $status
    }
    catch {
        return "NOT_FOUND"
    }
}

function Get-EKSEndpoint {
    try {
        $endpoint = aws eks describe-cluster --name fiso-eks-cluster --region $Region --query 'cluster.endpoint' --output text 2>$null
        return $endpoint
    }
    catch {
        return "None"
    }
}

function Get-RDSEndpoint {
    try {
        $endpoint = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region --query 'DBInstances[0].Endpoint.Address' --output text 2>$null
        return $endpoint
    }
    catch {
        return "None"
    }
}

function Show-InfrastructureStatus {
    $eksStatus = Get-EKSStatus
    $rdsStatus = Get-RDSStatus
    
    Clear-Host
    Write-Host "FISO AWS Infrastructure Status" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # EKS Status
    Write-Host "EKS Cluster (fiso-eks-cluster):" -ForegroundColor Yellow
    switch ($eksStatus) {
        "ACTIVE" { 
            Write-Success "✅ ACTIVE - Ready for deployment!"
            $endpoint = Get-EKSEndpoint
            Write-Host "   Endpoint: $endpoint" -ForegroundColor Gray
        }
        "CREATING" { 
            Write-Status "🔄 CREATING - Please wait..."
        }
        "FAILED" { 
            Write-Warning "❌ FAILED - Check CloudFormation console"
        }
        default { 
            Write-Info "⏳ Status: $eksStatus"
        }
    }
    
    Write-Host ""
    
    # RDS Status  
    Write-Host "RDS Database (fiso-postgres):" -ForegroundColor Yellow
    switch ($rdsStatus) {
        "available" { 
            Write-Success "✅ AVAILABLE - Ready for connections!"
            $endpoint = Get-RDSEndpoint
            Write-Host "   Endpoint: $endpoint" -ForegroundColor Gray
            Write-Host "   Connection: postgresql://fiso_user:fiso_password_123@$endpoint:5432/fiso_db" -ForegroundColor Gray
        }
        "creating" { 
            Write-Status "🔄 CREATING - Please wait..."
        }
        "configuring-enhanced-monitoring" { 
            Write-Status "🔄 CONFIGURING - Almost ready..."
        }
        "failed" { 
            Write-Warning "❌ FAILED - Check RDS console"
        }
        default { 
            Write-Info "⏳ Status: $rdsStatus"
        }
    }
    
    Write-Host ""
    
    # Overall Status
    if ($eksStatus -eq "ACTIVE" -and $rdsStatus -eq "available") {
        Write-Success "🎉 All infrastructure is ready for FISO deployment!"
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Update kubeconfig: aws eks update-kubeconfig --region $Region --name fiso-eks-cluster"
        Write-Host "2. Deploy FISO: .\deploy-k8s.ps1 deploy"
        Write-Host "3. Check status: .\deploy-k8s.ps1 status"
        return $true
    } else {
        Write-Info "⏳ Infrastructure still being created..."
        Write-Host "   EKS: $eksStatus | RDS: $rdsStatus"
        return $false
    }
}

# Main monitoring loop
Write-Info "Starting FISO AWS infrastructure monitoring..."
Write-Info "Press Ctrl+C to stop monitoring"
Write-Host ""

$isReady = $false
while (-not $isReady) {
    $isReady = Show-InfrastructureStatus
    
    if (-not $isReady) {
        Write-Host ""
        Write-Host "Checking again in $CheckInterval seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds $CheckInterval
    }
}

Write-Host ""
Write-Host "Monitoring complete - infrastructure is ready!" -ForegroundColor Green
