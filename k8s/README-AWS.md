# FISO AWS Deployment Guide

This guide helps you deploy FISO on AWS using EKS (Elastic Kubernetes Service) and RDS (Relational Database Service).

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** - [Install AWS CLI](https://aws.amazon.com/cli/)
2. **eksctl** - [Install eksctl](https://eksctl.io/installation/)
3. **kubectl** - [Install kubectl](https://kubernetes.io/docs/tasks/tools/)
4. **Helm** (optional, for Load Balancer Controller)

### AWS Configuration

```powershell
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret, Region (us-east-1), and output format (json)
```

### 1️⃣ Setup AWS Infrastructure

```powershell
# Navigate to k8s directory
cd k8s

# Setup EKS cluster and RDS database (takes ~20-30 minutes)
.\aws-setup.ps1 setup
```

This will create:
- EKS cluster with 2 worker nodes (t3.medium)
- RDS PostgreSQL instance (db.t3.micro)
- VPC and networking configuration
- AWS Load Balancer Controller

### 2️⃣ Deploy FISO Application

```powershell
# Deploy FISO to the EKS cluster
.\aws-setup.ps1 deploy
```

### 3️⃣ Check Status

```powershell
# Check AWS infrastructure status
.\aws-setup.ps1 status

# Check Kubernetes deployment status
.\deploy-k8s.ps1 status
```

## 📋 What Gets Created

### AWS Resources
- **EKS Cluster**: `fiso-eks-cluster` in us-east-1
- **Node Group**: 2-4 t3.medium instances
- **RDS Instance**: PostgreSQL 15.4 (db.t3.micro)
- **VPC**: Dedicated VPC with public/private subnets
- **Security Groups**: Configured for EKS and RDS communication
- **Application Load Balancer**: Internet-facing ALB for FISO API

### Kubernetes Resources
- **Deployment**: FISO API with 3 replicas
- **Service**: LoadBalancer service for external access
- **HPA**: Auto-scaling 2-10 pods based on CPU/memory
- **Monitoring**: Prometheus for metrics collection
- **Secrets**: AWS credentials and database connection
- **ConfigMap**: Application configuration

## 🔧 Configuration

### Database Connection
The RDS instance is automatically configured with:
- **Host**: Auto-generated RDS endpoint
- **Database**: `fiso_db`
- **Username**: `fiso_user`
- **Password**: `fiso_password_123` (update in production!)

### AWS Credentials
Your AWS credentials are stored in Kubernetes secrets and used for:
- Lambda function invocation
- Cost optimization APIs
- CloudWatch metrics

## 🌐 Access Your Application

After deployment, get the load balancer URL:

```powershell
# Get the external endpoint
kubectl get service fiso-api-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test the API
curl http://YOUR-ALB-ENDPOINT/health
```

## 📊 Monitoring

- **Prometheus**: Available at `http://YOUR-ALB-ENDPOINT/metrics`
- **Health Check**: `http://YOUR-ALB-ENDPOINT/health`
- **API Endpoint**: `http://YOUR-ALB-ENDPOINT/api/v1`

## 🧹 Cleanup

To remove all AWS resources:

```powershell
.\aws-setup.ps1 cleanup
```

⚠️ **Warning**: This will delete the EKS cluster, RDS instance, and all data!

## 💰 Cost Estimation

### Monthly AWS Costs (us-east-1):
- **EKS Cluster**: ~$72/month (control plane)
- **Worker Nodes**: ~$60/month (2 × t3.medium)
- **RDS Instance**: ~$13/month (db.t3.micro)
- **Load Balancer**: ~$16/month (ALB)
- **Total**: ~$161/month

### Cost Optimization Tips:
1. Use Spot instances for worker nodes
2. Schedule non-production workloads
3. Enable RDS automated backup deletion
4. Use smaller instance types for development

## 🔍 Troubleshooting

### Common Issues:

1. **kubectl not working**:
   ```powershell
   aws eks update-kubeconfig --region us-east-1 --name fiso-eks-cluster
   ```

2. **RDS connection issues**:
   - Check security groups allow port 5432
   - Verify RDS is in same VPC as EKS

3. **Load balancer not working**:
   - Ensure AWS Load Balancer Controller is installed
   - Check service annotations are correct

4. **Pod startup issues**:
   ```powershell
   kubectl logs -l app=fiso-api
   kubectl describe pod -l app=fiso-api
   ```

## 📞 Support

For issues with this deployment:
1. Check AWS CloudFormation events
2. Review EKS cluster logs
3. Verify IAM permissions
4. Check VPC and security group configurations

---

**Next Steps**: Once deployed, you can proceed with Phase 2 (ML Platform Integration) or Phase 3 (Cost Optimization).
