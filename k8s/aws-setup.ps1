# FISO AWS EKS Setup Script
# This script sets up AWS infrastructure for FISO deployment

param(
    [Parameter(Position=0)]
    [ValidateSet("setup", "deploy", "status", "cleanup", "help")]
    [string]$Action = "setup",
    
    [Parameter()]
    [string]$ClusterName = "fiso-eks-cluster",
    
    [Parameter()]
    [string]$Region = "us-east-1",
    
    [Parameter()]
    [string]$NodeGroup = "fiso-workers"
)

# Color output functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-AWSCli {
    Write-Info "Checking AWS CLI installation..."
    try {
        $awsVersion = aws --version 2>$null
        Write-Success "AWS CLI is available: $awsVersion"
        return $true
    }
    catch {
        Write-Error "AWS CLI is not installed. Please install AWS CLI first."
        return $false
    }
}

function Test-EKSCli {
    Write-Info "Checking eksctl installation..."
    try {
        # Try local eksctl first
        if (Test-Path ".\eksctl.exe") {
            $eksVersion = .\eksctl.exe version 2>$null
            Write-Success "eksctl is available: $eksVersion"
            return $true
        }
        # Try system PATH eksctl
        $eksVersion = eksctl version 2>$null
        Write-Success "eksctl is available: $eksVersion"
        return $true
    }
    catch {
        Write-Error "eksctl is not installed. Please install eksctl first."
        return $false
    }
}

function Test-AWSCredentials {
    Write-Info "Checking AWS credentials..."
    try {
        $identity = aws sts get-caller-identity --output text --query 'Account' 2>$null
        Write-Success "AWS credentials are configured for account: $identity"
        return $true
    }
    catch {
        Write-Error "AWS credentials not configured. Run 'aws configure' first."
        return $false
    }
}

function New-EKSCluster {
    Write-Info "Creating EKS cluster '$ClusterName' in region '$Region'..."
    
    $clusterExists = aws eks describe-cluster --name $ClusterName --region $Region 2>$null
    if ($clusterExists) {
        Write-Warning "EKS cluster '$ClusterName' already exists"
        return $true
    }
    
    try {
        Write-Info "This will take 10-15 minutes..."
        if (Test-Path ".\eksctl.exe") {
            .\eksctl.exe create cluster `
                --name $ClusterName `
                --region $Region `
                --version 1.30 `
                --nodegroup-name $NodeGroup `
                --node-type t3.medium `
                --nodes 2 `
                --nodes-min 1 `
                --nodes-max 4 `
                --managed
        } else {
            eksctl create cluster `
                --name $ClusterName `
                --region $Region `
                --version 1.30 `
                --nodegroup-name $NodeGroup `
                --node-type t3.medium `
                --nodes 2 `
                --nodes-min 1 `
                --nodes-max 4 `
                --managed
        }
            
        Write-Success "EKS cluster created successfully"
        return $true
    }
    catch {
        Write-Error "Failed to create EKS cluster: $_"
        return $false
    }
}

function New-RDSInstance {
    Write-Info "Creating RDS PostgreSQL instance..."
    
    $dbExists = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region 2>$null
    if ($dbExists) {
        Write-Warning "RDS instance 'fiso-postgres' already exists"
        return $true
    }
    
    try {
        # Create DB subnet group first
        Write-Info "Creating DB subnet group..."
        aws rds create-db-subnet-group `
            --db-subnet-group-name fiso-db-subnet-group `
            --db-subnet-group-description "FISO Database Subnet Group" `
            --subnet-ids (aws ec2 describe-subnets --filters "Name=vpc-id,Values=$(aws eks describe-cluster --name $ClusterName --region $Region --query 'cluster.resourcesVpcConfig.vpcId' --output text)" --query 'Subnets[*].SubnetId' --output text).Split("`t") `
            --region $Region
        
        # Create RDS instance
        Write-Info "Creating RDS PostgreSQL instance (this may take 10-15 minutes)..."
        aws rds create-db-instance `
            --db-instance-identifier fiso-postgres `
            --db-instance-class db.t3.micro `
            --engine postgres `
            --engine-version 15.4 `
            --master-username fiso_user `
            --master-user-password fiso_password_123 `
            --allocated-storage 20 `
            --storage-type gp2 `
            --db-name fiso_db `
            --db-subnet-group-name fiso-db-subnet-group `
            --vpc-security-group-ids (aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$(aws eks describe-cluster --name $ClusterName --region $Region --query 'cluster.resourcesVpcConfig.vpcId' --output text)" "Name=group-name,Values=default" --query 'SecurityGroups[0].GroupId' --output text) `
            --region $Region
            
        Write-Success "RDS instance creation initiated"
        return $true
    }
    catch {
        Write-Error "Failed to create RDS instance: $_"
        return $false
    }
}

function Update-KubeConfig {
    Write-Info "Updating kubeconfig for EKS cluster..."
    
    try {
        aws eks update-kubeconfig --region $Region --name $ClusterName
        Write-Success "Kubeconfig updated successfully"
        return $true
    }
    catch {
        Write-Error "Failed to update kubeconfig: $_"
        return $false
    }
}

function Install-AWSLoadBalancerController {
    Write-Info "Installing AWS Load Balancer Controller..."
    
    try {
        # Create IAM OIDC identity provider
        eksctl utils associate-iam-oidc-provider --region $Region --cluster $ClusterName --approve
        
        # Download IAM policy
        curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json
        
        # Create IAM policy
        aws iam create-policy `
            --policy-name AWSLoadBalancerControllerIAMPolicy `
            --policy-document file://iam_policy.json
        
        # Create service account
        eksctl create iamserviceaccount `
            --cluster=$ClusterName `
            --namespace=kube-system `
            --name=aws-load-balancer-controller `
            --role-name AmazonEKSLoadBalancerControllerRole `
            --attach-policy-arn=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy `
            --approve
        
        # Install AWS Load Balancer Controller
        helm repo add eks https://aws.github.io/eks-charts
        helm repo update
        helm install aws-load-balancer-controller eks/aws-load-balancer-controller `
            -n kube-system `
            --set clusterName=$ClusterName `
            --set serviceAccount.create=false `
            --set serviceAccount.name=aws-load-balancer-controller
        
        Write-Success "AWS Load Balancer Controller installed"
        return $true
    }
    catch {
        Write-Warning "AWS Load Balancer Controller installation failed, but cluster is still usable"
        return $true
    }
}

function Get-AWSStatus {
    Write-Info "Getting AWS infrastructure status..."
    
    Write-Host ""
    Write-Host "AWS Infrastructure Status" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    # EKS Cluster Status
    Write-Host ""
    Write-Host "EKS Cluster:" -ForegroundColor Yellow
    aws eks describe-cluster --name $ClusterName --region $Region --query 'cluster.{Name:name,Status:status,Version:version,Endpoint:endpoint}' --output table
    
    # RDS Status
    Write-Host ""
    Write-Host "RDS Instance:" -ForegroundColor Yellow
    aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region --query 'DBInstances[0].{Identifier:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Endpoint:Endpoint.Address}' --output table
    
    # Node Group Status
    Write-Host ""
    Write-Host "Node Groups:" -ForegroundColor Yellow
    aws eks describe-nodegroup --cluster-name $ClusterName --nodegroup-name $NodeGroup --region $Region --query 'nodegroup.{Name:nodegroupName,Status:status,InstanceTypes:instanceTypes,ScalingConfig:scalingConfig}' --output table
}

function Remove-AWSInfrastructure {
    Write-Warning "This will delete ALL AWS infrastructure for FISO!"
    $confirmation = Read-Host "Type 'DELETE' to confirm"
    
    if ($confirmation -ne "DELETE") {
        Write-Info "Cleanup cancelled"
        return
    }
    
    try {
        Write-Info "Deleting RDS instance..."
        aws rds delete-db-instance --db-instance-identifier fiso-postgres --skip-final-snapshot --region $Region
        
        Write-Info "Deleting EKS cluster..."
        eksctl delete cluster --name $ClusterName --region $Region
        
        Write-Info "Deleting DB subnet group..."
        aws rds delete-db-subnet-group --db-subnet-group-name fiso-db-subnet-group --region $Region
        
        Write-Success "AWS infrastructure cleanup initiated"
    }
    catch {
        Write-Error "Error during cleanup: $_"
    }
}

function Set-AWSInfrastructure {
    Write-Info "Setting up AWS infrastructure for FISO..."
    
    # Pre-flight checks
    if (!(Test-AWSCli)) { return }
    if (!(Test-EKSCli)) { return }
    if (!(Test-AWSCredentials)) { return }
    
    # Create infrastructure
    if (!(New-EKSCluster)) { return }
    if (!(Update-KubeConfig)) { return }
    if (!(New-RDSInstance)) { return }
    Install-AWSLoadBalancerController
    
    # Show status
    Get-AWSStatus
    
    Write-Success "AWS infrastructure setup completed!"
    Write-Info "You can now run: .\deploy-k8s.ps1 deploy"
}

function Show-Help {
    Write-Host "FISO AWS EKS Setup Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\aws-setup.ps1 [command] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  setup    - Create EKS cluster and RDS instance (default)"
    Write-Host "  deploy   - Deploy FISO to existing cluster"
    Write-Host "  status   - Show AWS infrastructure status"
    Write-Host "  cleanup  - Delete all AWS infrastructure"
    Write-Host "  help     - Show this help message"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -ClusterName  - EKS cluster name (default: fiso-eks-cluster)"
    Write-Host "  -Region       - AWS region (default: us-east-1)"
    Write-Host "  -NodeGroup    - Node group name (default: fiso-workers)"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\aws-setup.ps1 setup"
    Write-Host "  .\aws-setup.ps1 status"
    Write-Host "  .\aws-setup.ps1 deploy"
}

# Main script logic
switch ($Action) {
    "setup" {
        Set-AWSInfrastructure
    }
    "deploy" {
        if (Test-AWSCli -and Test-AWSCredentials) {
            Update-KubeConfig
            Write-Info "Running Kubernetes deployment..."
            & ".\deploy-k8s.ps1" deploy
        }
    }
    "status" {
        if (Test-AWSCli -and Test-AWSCredentials) {
            Get-AWSStatus
        }
    }
    "cleanup" {
        Remove-AWSInfrastructure
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Action"
        Show-Help
    }
}
