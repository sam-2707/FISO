# Simple EC2 Docker Deployment for FISO
Write-Host "Deploying FISO to EC2 with Docker..." -ForegroundColor Cyan

# Configuration
$instanceType = "t3.medium"
$securityGroup = "fiso-docker-sg"
$keyName = "fiso-keypair"

Write-Host "Creating security group..." -ForegroundColor Yellow
$sgResult = aws ec2 create-security-group --group-name $securityGroup --description "FISO Docker Security Group" --region us-east-1 2>&1

if ($LASTEXITCODE -eq 0) {
    $sgId = ($sgResult | ConvertFrom-Json).GroupId
    Write-Host "Security group created: $sgId" -ForegroundColor Green
    
    # Add rules
    aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-1 > $null 2>&1
    aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 8080 --cidr 0.0.0.0/0 --region us-east-1 > $null 2>&1
    aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1 > $null 2>&1
} else {
    # Try to get existing security group
    $sgId = aws ec2 describe-security-groups --group-names $securityGroup --region us-east-1 --query 'SecurityGroups[0].GroupId' --output text 2>$null
    if ($sgId -and $sgId -ne "None") {
        Write-Host "Using existing security group: $sgId" -ForegroundColor Green
    } else {
        Write-Host "Failed to create or find security group" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Launching EC2 instance..." -ForegroundColor Yellow

# Simple instance launch
$launchResult = aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --count 1 --instance-type $instanceType --key-name $keyName --security-group-ids $sgId --region us-east-1

if ($LASTEXITCODE -eq 0) {
    $instanceId = ($launchResult | ConvertFrom-Json).Instances[0].InstanceId
    Write-Host "Instance launched: $instanceId" -ForegroundColor Green
    
    Write-Host "Waiting for instance to start..." -ForegroundColor Yellow
    aws ec2 wait instance-running --instance-ids $instanceId --region us-east-1
    
    $publicIp = aws ec2 describe-instances --instance-ids $instanceId --region us-east-1 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
    
    Write-Host "SUCCESS! Instance is running" -ForegroundColor Green
    Write-Host "Instance ID: $instanceId" -ForegroundColor Cyan
    Write-Host "Public IP: $publicIp" -ForegroundColor Cyan
    Write-Host "SSH Command: ssh -i $keyName.pem ec2-user@$publicIp" -ForegroundColor Yellow
    
    Write-Host "`nTo deploy FISO Docker container, SSH to the instance and run:" -ForegroundColor Blue
    Write-Host "sudo yum update -y && sudo yum install -y docker" -ForegroundColor Gray
    Write-Host "sudo systemctl start docker && sudo systemctl enable docker" -ForegroundColor Gray
    Write-Host "sudo usermod -a -G docker ec2-user" -ForegroundColor Gray
    Write-Host "aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 412374076384.dkr.ecr.us-east-1.amazonaws.com" -ForegroundColor Gray
    Write-Host "sudo docker run -d -p 8080:8080 --name fiso-app 412374076384.dkr.ecr.us-east-1.amazonaws.com/fiso-api:latest" -ForegroundColor Gray
    
    Write-Host "`nAfter setup, FISO will be available at: http://$publicIp:8080" -ForegroundColor Cyan
} else {
    Write-Host "Failed to launch instance" -ForegroundColor Red
    Write-Host $launchResult -ForegroundColor Red
}
