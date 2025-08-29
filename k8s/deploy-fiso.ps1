# FISO AWS Deployment Script with Security
# This script handles secure deployment with local credentials

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "status", "cleanup", "help")]
    [string]$Action = "deploy"
)

function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-LocalSecrets {
    Write-Info "Checking for local secrets file..."
    
    if (!(Test-Path "fiso-secrets.local.yaml")) {
        Write-Error "Local secrets file not found!"
        Write-Host ""
        Write-Host "Please create 'fiso-secrets.local.yaml' with your AWS credentials:" -ForegroundColor Yellow
        Write-Host "1. Copy fiso-secrets.yaml to fiso-secrets.local.yaml"
        Write-Host "2. Replace YOUR_AWS_ACCESS_KEY_ID with your actual access key"
        Write-Host "3. Replace YOUR_AWS_SECRET_ACCESS_KEY with your actual secret key"
        Write-Host "4. Replace YOUR_RDS_ENDPOINT with the actual RDS endpoint"
        Write-Host ""
        Write-Host "The .local.yaml file is in .gitignore and won't be committed to Git" -ForegroundColor Green
        return $false
    }
    
    Write-Success "Local secrets file found"
    return $true
}

function Update-RDSEndpoint {
    Write-Info "Getting RDS endpoint..."
    
    try {
        $rdsEndpoint = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region us-east-1 --query 'DBInstances[0].Endpoint.Address' --output text 2>$null
        
        if ($rdsEndpoint -and $rdsEndpoint -ne "None") {
            Write-Info "Found RDS endpoint: $rdsEndpoint"
            
            # Update the local secrets file with the real RDS endpoint
            $content = Get-Content "fiso-secrets.local.yaml" -Raw
            $updatedContent = $content -replace "YOUR_RDS_ENDPOINT_WILL_BE_UPDATED", $rdsEndpoint
            Set-Content "fiso-secrets.local.yaml" -Value $updatedContent
            
            Write-Success "Updated local secrets with RDS endpoint"
            return $true
        } else {
            Write-Warning "RDS endpoint not available yet. Please wait for RDS to be ready."
            return $false
        }
    }
    catch {
        Write-Error "Failed to get RDS endpoint: $_"
        return $false
    }
}

function Deploy-FISO-Secure {
    Write-Info "Starting secure FISO deployment..."
    
    # Check prerequisites
    if (!(Test-LocalSecrets)) { return }
    if (!(Update-RDSEndpoint)) { return }
    
    # Check EKS cluster is ready
    $eksStatus = aws eks describe-cluster --name fiso-eks-cluster --region us-east-1 --query 'cluster.status' --output text 2>$null
    if ($eksStatus -ne "ACTIVE") {
        Write-Error "EKS cluster is not ready. Status: $eksStatus"
        Write-Info "Please wait for EKS cluster to be ACTIVE before deploying"
        return
    }
    
    # Update kubeconfig
    Write-Info "Updating kubeconfig..."
    aws eks update-kubeconfig --region us-east-1 --name fiso-eks-cluster
    
    # Deploy using local secrets
    Write-Info "Deploying FISO with local secrets..."
    kubectl apply -f fiso-secrets.local.yaml
    kubectl apply -f fiso-deployment.yaml
    kubectl apply -f fiso-monitoring.yaml
    kubectl apply -f fiso-ingress.yaml
    
    Write-Success "FISO deployed successfully!"
    
    # Show status
    Write-Info "Getting deployment status..."
    Start-Sleep -Seconds 5
    kubectl get pods -l app=fiso-api
    kubectl get services -l app=fiso-api
}

function Get-FISO-Status {
    Write-Info "Getting FISO deployment status..."
    
    Write-Host ""
    Write-Host "FISO Deployment Status" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    
    # EKS Status
    $eksStatus = aws eks describe-cluster --name fiso-eks-cluster --region us-east-1 --query 'cluster.status' --output text 2>$null
    Write-Host "EKS Cluster: $eksStatus" -ForegroundColor Yellow
    
    # RDS Status
    $rdsStatus = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region us-east-1 --query 'DBInstances[0].DBInstanceStatus' --output text 2>$null
    Write-Host "RDS Database: $rdsStatus" -ForegroundColor Yellow
    
    if ($eksStatus -eq "ACTIVE") {
        Write-Host ""
        Write-Host "Pods:" -ForegroundColor Yellow
        kubectl get pods -l app=fiso-api -o wide
        
        Write-Host ""
        Write-Host "Services:" -ForegroundColor Yellow
        kubectl get services -l app=fiso-api
        
        Write-Host ""
        Write-Host "Ingress:" -ForegroundColor Yellow
        kubectl get ingress fiso-ingress
    }
}

function Remove-FISO {
    Write-Warning "Cleaning up FISO deployment..."
    
    try {
        kubectl delete -f fiso-ingress.yaml --ignore-not-found=true
        kubectl delete -f fiso-monitoring.yaml --ignore-not-found=true
        kubectl delete -f fiso-deployment.yaml --ignore-not-found=true
        kubectl delete -f fiso-secrets.local.yaml --ignore-not-found=true
        Write-Success "FISO cleanup completed"
    }
    catch {
        Write-Error "Error during cleanup: $_"
    }
}

function Show-Help {
    Write-Host "FISO Secure AWS Deployment Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy-fiso.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  deploy   - Deploy FISO using local secrets (default)"
    Write-Host "  status   - Show deployment status"
    Write-Host "  cleanup  - Remove FISO deployment"
    Write-Host "  help     - Show this help message"
    Write-Host ""
    Write-Host "Security:" -ForegroundColor Yellow
    Write-Host "  This script uses fiso-secrets.local.yaml for credentials"
    Write-Host "  The local file is excluded from Git commits"
    Write-Host "  RDS endpoint is automatically updated when available"
}

# Main script logic
switch ($Action) {
    "deploy" {
        Deploy-FISO-Secure
    }
    "status" {
        Get-FISO-Status
    }
    "cleanup" {
        Remove-FISO
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Action"
        Show-Help
    }
}
