# FISO Kubernetes Deployment PowerShell Script
# This script deploys FISO to Kubernetes cluster across multiple cloud providers

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "status", "cleanup", "help")]
    [string]$Action = "deploy"
)

# Color output functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-KubectlInstalled {
    Write-Info "Checking kubectl installation..."
    try {
        $null = kubectl version --client --short 2>$null
        Write-Success "kubectl is available"
        return $true
    }
    catch {
        Write-Error "kubectl is not installed. Please install kubectl first."
        return $false
    }
}

function Test-ClusterConnection {
    Write-Info "Checking cluster connection..."
    try {
        $clusterInfo = kubectl cluster-info 2>$null | Select-Object -First 1
        Write-Success "Connected to cluster: $clusterInfo"
        return $true
    }
    catch {
        Write-Error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        return $false
    }
}

function Deploy-Secrets {
    Write-Info "Deploying FISO secrets..."
    
    if (!(Test-Path "fiso-secrets.yaml")) {
        Write-Error "fiso-secrets.yaml not found. Please ensure all YAML files are present."
        return $false
    }
    
    try {
        kubectl apply -f fiso-secrets.yaml
        Write-Success "Secrets deployed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to deploy secrets: $_"
        return $false
    }
}

function Deploy-Application {
    Write-Info "Deploying FISO application..."
    
    try {
        kubectl apply -f fiso-deployment.yaml
        Write-Success "Application deployment created"
        
        Write-Info "Waiting for deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/fiso-api
        Write-Success "Application is ready"
        return $true
    }
    catch {
        Write-Error "Failed to deploy application: $_"
        return $false
    }
}

function Deploy-Monitoring {
    Write-Info "Deploying monitoring stack..."
    
    try {
        kubectl apply -f fiso-monitoring.yaml
        Write-Success "Monitoring stack deployed"
        
        Write-Info "Waiting for Prometheus to be ready..."
        kubectl wait --for=condition=available --timeout=180s deployment/fiso-prometheus
        Write-Success "Monitoring is ready"
        return $true
    }
    catch {
        Write-Error "Failed to deploy monitoring: $_"
        return $false
    }
}

function Deploy-Ingress {
    Write-Info "Deploying ingress configuration..."
    
    try {
        kubectl apply -f fiso-ingress.yaml
        Write-Success "Ingress deployed"
        return $true
    }
    catch {
        Write-Error "Failed to deploy ingress: $_"
        return $false
    }
}

function Get-DeploymentStatus {
    Write-Info "Getting deployment status..."
    
    Write-Host ""
    Write-Host "FISO Deployment Status" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Pods:" -ForegroundColor Yellow
    kubectl get pods -l app=fiso-api -o wide
    
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    kubectl get services -l app=fiso-api
    
    Write-Host ""
    Write-Host "Ingress:" -ForegroundColor Yellow
    kubectl get ingress fiso-ingress
    
    # Get external IP
    try {
        $externalIP = kubectl get service fiso-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
        if ([string]::IsNullOrEmpty($externalIP)) {
            $externalIP = "Pending"
        }
    }
    catch {
        $externalIP = "Pending"
    }
    
    Write-Host ""
    Write-Host "External Access:" -ForegroundColor Cyan
    Write-Host "IP Address: $externalIP"
    Write-Host "Health Check: http://$externalIP/health"
    Write-Host "API Endpoint: http://$externalIP/api/v1"
    Write-Host "Metrics: http://$externalIP/metrics"
}

function Deploy-FISO {
    Write-Info "Starting FISO Kubernetes deployment..."
    
    # Pre-flight checks
    if (!(Test-KubectlInstalled)) { return }
    if (!(Test-ClusterConnection)) { return }
    
    # Deploy components
    if (!(Deploy-Secrets)) { return }
    if (!(Deploy-Application)) { return }
    if (!(Deploy-Monitoring)) { return }
    if (!(Deploy-Ingress)) { return }
    
    # Show status
    Get-DeploymentStatus
    
    Write-Success "FISO deployment completed successfully!"
    Write-Info "Access your FISO API at the external IP shown above"
}

function Remove-FISO {
    Write-Warning "Cleaning up FISO deployment..."
    
    try {
        kubectl delete -f fiso-ingress.yaml --ignore-not-found=true
        kubectl delete -f fiso-monitoring.yaml --ignore-not-found=true
        kubectl delete -f fiso-deployment.yaml --ignore-not-found=true
        kubectl delete -f fiso-secrets.yaml --ignore-not-found=true
        Write-Success "Cleanup completed"
    }
    catch {
        Write-Error "Error during cleanup: $_"
    }
}

function Show-Help {
    Write-Host "FISO Kubernetes Deployment PowerShell Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy-k8s.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  deploy   - Deploy FISO to Kubernetes (default)"
    Write-Host "  status   - Show deployment status"
    Write-Host "  cleanup  - Remove FISO deployment"
    Write-Host "  help     - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy-k8s.ps1 deploy"
    Write-Host "  .\deploy-k8s.ps1 status"
    Write-Host "  .\deploy-k8s.ps1 cleanup"
}

# Main script logic
switch ($Action) {
    "deploy" {
        Deploy-FISO
    }
    "status" {
        if (Test-KubectlInstalled -and Test-ClusterConnection) {
            Get-DeploymentStatus
        }
    }
    "cleanup" {
        Remove-FISO
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Action"
        Write-Host "Use .\deploy-k8s.ps1 help for usage information"
    }
}
