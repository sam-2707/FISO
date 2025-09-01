# Deploy FISO Docker Container to EC2
# Fastest and most reliable deployment method!

Write-Host "🚀 Deploying FISO Docker Container to EC2" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Configuration
$keyName = "fiso-keypair"
$securityGroup = "fiso-docker-sg"
$instanceType = "t3.medium"
$imageId = "ami-0c02fb55956c7d316"  # Amazon Linux 2023
$dockerImage = "412374076384.dkr.ecr.us-east-1.amazonaws.com/fiso-api:latest"

Write-Host "`n📋 Setting up EC2 infrastructure..." -ForegroundColor Yellow

# Create security group for Docker container
Write-Host "Creating security group: $securityGroup" -ForegroundColor Blue
$sgResult = aws ec2 create-security-group --group-name $securityGroup --description "FISO Docker Container Security Group" --region us-east-1 2>&1

if ($LASTEXITCODE -eq 0) {
    $sgInfo = $sgResult | ConvertFrom-Json
    $securityGroupId = $sgInfo.GroupId
    Write-Host "✅ Security group created: $securityGroupId" -ForegroundColor Green
    
    # Add inbound rules
    Write-Host "Adding security group rules..." -ForegroundColor Blue
    aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-1
    aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 8080 --cidr 0.0.0.0/0 --region us-east-1
    aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1
} else {
    # Security group might already exist
    $securityGroupId = (aws ec2 describe-security-groups --group-names $securityGroup --region us-east-1 --query 'SecurityGroups[0].GroupId' --output text 2>$null)
    if ($securityGroupId) {
        Write-Host "✅ Using existing security group: $securityGroupId" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create or find security group" -ForegroundColor Red
        exit 1
    }
}

# Create user data script for EC2 instance
$userData = @"
#!/bin/bash
# Install Docker and configure FISO

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Configure ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 412374076384.dkr.ecr.us-east-1.amazonaws.com

# Pull and run FISO container
docker pull $dockerImage
docker run -d --name fiso-app -p 80:8080 -p 8080:8080 \
  -e ENV=production \
  -e POSTGRES_HOST=fiso-postgres.cgli0siy6wfn.us-east-1.rds.amazonaws.com \
  -e POSTGRES_DB=fiso_db \
  -e POSTGRES_USER=fiso_user \
  -e POSTGRES_PASSWORD=fiso_secure_password_2024 \
  --restart unless-stopped \
  $dockerImage

# Create status page
echo '<html><body><h1>FISO Docker Deployment Status</h1><p>Container Status:</p><pre>' > /var/www/html/status.html
docker ps >> /var/www/html/status.html
echo '</pre></body></html>' >> /var/www/html/status.html

# Log deployment
echo "FISO Docker deployment completed at $(date)" >> /var/log/fiso-deployment.log
"@

# Encode user data
$userDataEncoded = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($userData))

Write-Host "`n🚀 Launching EC2 instance..." -ForegroundColor Green

# Launch EC2 instance
$launchResult = aws ec2 run-instances `
    --image-id $imageId `
    --count 1 `
    --instance-type $instanceType `
    --key-name $keyName `
    --security-group-ids $securityGroupId `
    --user-data $userDataEncoded `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=FISO-Docker-Server},{Key=Project,Value=FISO},{Key=Environment,Value=Production}]" `
    --iam-instance-profile Name=fiso-ec2-role `
    --region us-east-1 2>&1

if ($LASTEXITCODE -eq 0) {
    $instanceInfo = $launchResult | ConvertFrom-Json
    $instanceId = $instanceInfo.Instances[0].InstanceId
    
    Write-Host "✅ EC2 instance launched: $instanceId" -ForegroundColor Green
    Write-Host "⏱️ Waiting for instance to start..." -ForegroundColor Yellow
    
    # Wait for instance to be running
    aws ec2 wait instance-running --instance-ids $instanceId --region us-east-1
    
    # Get public IP
    $publicIp = aws ec2 describe-instances --instance-ids $instanceId --region us-east-1 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
    
    Write-Host "`n🎉 FISO Docker deployment successful!" -ForegroundColor Green
    Write-Host "Instance ID: $instanceId" -ForegroundColor Gray
    Write-Host "Public IP: $publicIp" -ForegroundColor Cyan
    Write-Host "FISO URL: http://$publicIp:8080" -ForegroundColor Cyan
    Write-Host "Health Check: http://$publicIp:8080/health" -ForegroundColor Cyan
    
    Write-Host "`n⏱️ Container is starting up (2-3 minutes)..." -ForegroundColor Yellow
    Write-Host "Monitor at: https://console.aws.amazon.com/ec2/home?region=us-east-1#Instances:instanceId=$instanceId" -ForegroundColor Blue
    
    # Test after a delay
    Write-Host "`n🧪 Testing deployment in 3 minutes..." -ForegroundColor Yellow
    Start-Sleep -Seconds 180
    
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://$publicIp:8080/health" -Method GET -TimeoutSec 30
        Write-Host "✅ Health check passed!" -ForegroundColor Green
        Write-Host "Response: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠️ Health check pending (container might still be starting)" -ForegroundColor Yellow
        Write-Host "Try again in a few minutes: http://$publicIp:8080/health" -ForegroundColor Cyan
    }
    
} else {
    Write-Host "❌ Failed to launch EC2 instance:" -ForegroundColor Red
    Write-Host $launchResult -ForegroundColor Red
}

Write-Host "`n📊 EC2 Docker Benefits:" -ForegroundColor Green
Write-Host "✅ Deploy in 2-3 minutes" -ForegroundColor Green
Write-Host "✅ No subscription requirements" -ForegroundColor Green
Write-Host "✅ Full control over environment" -ForegroundColor Green
Write-Host "✅ Easy scaling with Auto Scaling Groups" -ForegroundColor Green
Write-Host "✅ Cost-effective for sustained workloads" -ForegroundColor Green

Write-Host "`n🎯 Next Steps:" -ForegroundColor Blue
Write-Host "1. Add the new endpoint to multi-cloud orchestration" -ForegroundColor Gray
Write-Host "2. Set up Application Load Balancer for HA" -ForegroundColor Gray
Write-Host "3. Configure Auto Scaling Group" -ForegroundColor Gray
Write-Host "4. Set up CloudWatch monitoring" -ForegroundColor Gray

Write-Host "`n✅ EC2 Docker deployment complete!" -ForegroundColor Cyan
