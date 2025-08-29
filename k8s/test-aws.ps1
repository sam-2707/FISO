# FISO AWS Lambda Test Script
# Tests the AWS Lambda function deployment

param(
    [Parameter()]
    [string]$Region = "us-east-1"
)

function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-AWSLambda {
    Write-Info "Testing AWS Lambda function..."
    
    try {
        # Get Lambda function URL
        $functionUrl = aws lambda get-function-url-config --function-name fiso_sample_app_py --region $Region --query 'FunctionUrl' --output text 2>$null
        
        if ($functionUrl -and $functionUrl -ne "None") {
            Write-Info "Found Lambda function URL: $functionUrl"
            
            # Test the function
            $response = Invoke-RestMethod -Uri $functionUrl -Method GET -ErrorAction Stop
            
            if ($response) {
                Write-Success "Lambda function is working!"
                Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Green
                return $true
            }
        } else {
            Write-Warning "Lambda function URL not found. Testing with AWS CLI invoke..."
            
            # Test with CLI invoke
            aws lambda invoke --function-name fiso_sample_app_py --region $Region response.json
            
            if (Test-Path "response.json") {
                $response = Get-Content "response.json" | ConvertFrom-Json
                Write-Success "Lambda function is working!"
                Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Green
                Remove-Item "response.json" -Force
                return $true
            }
        }
    }
    catch {
        Write-Error "Lambda function test failed: $_"
        return $false
    }
}

function Test-EKSConnection {
    Write-Info "Testing EKS cluster connection..."
    
    try {
        # First check if cluster exists
        $clusterStatus = aws eks describe-cluster --name fiso-eks-cluster --region $Region --query 'cluster.status' --output text 2>$null
        
        if ($clusterStatus -eq "ACTIVE") {
            $nodes = kubectl get nodes --no-headers 2>$null
            if ($nodes) {
                $nodeCount = ($nodes | Measure-Object).Count
                Write-Success "EKS cluster is accessible with $nodeCount nodes"
                return $true
            } else {
                Write-Warning "EKS cluster exists but kubectl not configured. Updating kubeconfig..."
                aws eks update-kubeconfig --region $Region --name fiso-eks-cluster
                
                # Test again after kubeconfig update
                $nodes = kubectl get nodes --no-headers 2>$null
                if ($nodes) {
                    $nodeCount = ($nodes | Measure-Object).Count
                    Write-Success "EKS cluster is accessible with $nodeCount nodes"
                    return $true
                } else {
                    Write-Error "kubectl still not working after kubeconfig update"
                    return $false
                }
            }
        } elseif ($clusterStatus) {
            Write-Warning "EKS cluster exists but status is: $clusterStatus"
            return $false
        } else {
            Write-Warning "EKS cluster 'fiso-eks-cluster' does not exist"
            Write-Info "Run '.\aws-setup.ps1 setup' to create the cluster"
            return $false
        }
    }
    catch {
        Write-Warning "EKS cluster 'fiso-eks-cluster' does not exist"
        Write-Info "Run '.\aws-setup.ps1 setup' to create the cluster"
        return $false
    }
}

function Test-RDSConnection {
    Write-Info "Testing RDS instance..."
    
    try {
        $rdsStatus = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region --query 'DBInstances[0].DBInstanceStatus' --output text 2>$null
        
        if ($rdsStatus -eq "available") {
            Write-Success "RDS instance is available"
            
            $endpoint = aws rds describe-db-instances --db-instance-identifier fiso-postgres --region $Region --query 'DBInstances[0].Endpoint.Address' --output text
            Write-Info "RDS Endpoint: $endpoint"
            return $true
        } elseif ($rdsStatus) {
            Write-Warning "RDS instance status: $rdsStatus (may still be starting up)"
            return $true
        } else {
            Write-Error "RDS instance not found"
            return $false
        }
    }
    catch {
        Write-Error "RDS test failed: $_"
        return $false
    }
}

function Show-AWSResources {
    Write-Host ""
    Write-Host "AWS Resources Summary" -ForegroundColor Cyan
    Write-Host "====================" -ForegroundColor Cyan
    
    # Lambda Functions
    Write-Host ""
    Write-Host "Lambda Functions:" -ForegroundColor Yellow
    aws lambda list-functions --region $Region --query 'Functions[?starts_with(FunctionName, `fiso`)].{Name:FunctionName,Runtime:Runtime,LastModified:LastModified}' --output table
    
    # EKS Clusters
    Write-Host ""
    Write-Host "EKS Clusters:" -ForegroundColor Yellow
    aws eks list-clusters --region $Region --query 'clusters' --output table
    
    # RDS Instances
    Write-Host ""
    Write-Host "RDS Instances:" -ForegroundColor Yellow
    aws rds describe-db-instances --region $Region --query 'DBInstances[?starts_with(DBInstanceIdentifier, `fiso`)].{Name:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Class:DBInstanceClass}' --output table
}

# Main execution
Write-Info "Running FISO AWS Integration Tests..."

$allPassed = $true

# Test AWS Lambda
if (!(Test-AWSLambda)) { $allPassed = $false }

# Test EKS if exists
if (!(Test-EKSConnection)) { $allPassed = $false }

# Test RDS if exists  
if (!(Test-RDSConnection)) { $allPassed = $false }

# Show resource summary
Show-AWSResources

if ($allPassed) {
    Write-Success "All AWS tests passed! FISO is ready for deployment."
} else {
    Write-Warning "Some tests failed. Please check the issues above."
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. If Lambda is working: Your function layer is ready"
Write-Host "2. If EKS is ready: Run .\deploy-k8s.ps1 deploy"
Write-Host "3. If RDS is available: Database layer is ready"
Write-Host "4. Full deployment: .\aws-setup.ps1 deploy"
