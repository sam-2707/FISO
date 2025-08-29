#!/bin/bash

# FISO Kubernetes Deployment Script
# This script deploys FISO to Kubernetes cluster across multiple cloud providers

set -e

echo "🚀 FISO Kubernetes Deployment Script"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    print_success "kubectl is available"
}

# Check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    CLUSTER_INFO=$(kubectl cluster-info | head -1)
    print_success "Connected to cluster: $CLUSTER_INFO"
}

# Deploy FISO secrets
deploy_secrets() {
    print_status "Deploying FISO secrets..."
    
    # Check if secrets file exists
    if [[ ! -f "fiso-secrets.yaml" ]]; then
        print_error "fiso-secrets.yaml not found. Please ensure all YAML files are present."
        exit 1
    fi
    
    # Apply secrets
    kubectl apply -f fiso-secrets.yaml
    print_success "Secrets deployed successfully"
}

# Deploy FISO application
deploy_application() {
    print_status "Deploying FISO application..."
    
    # Apply deployment
    kubectl apply -f fiso-deployment.yaml
    print_success "Application deployment created"
    
    # Wait for deployment to be ready
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/fiso-api
    print_success "Application is ready"
}

# Deploy monitoring
deploy_monitoring() {
    print_status "Deploying monitoring stack..."
    
    kubectl apply -f fiso-monitoring.yaml
    print_success "Monitoring stack deployed"
    
    # Wait for Prometheus to be ready
    print_status "Waiting for Prometheus to be ready..."
    kubectl wait --for=condition=available --timeout=180s deployment/fiso-prometheus
    print_success "Monitoring is ready"
}

# Deploy ingress
deploy_ingress() {
    print_status "Deploying ingress configuration..."
    
    kubectl apply -f fiso-ingress.yaml
    print_success "Ingress deployed"
}

# Get deployment status
get_status() {
    print_status "Getting deployment status..."
    
    echo ""
    echo "📊 FISO Deployment Status"
    echo "========================"
    
    # Get pods
    echo "Pods:"
    kubectl get pods -l app=fiso-api -o wide
    
    echo ""
    echo "Services:"
    kubectl get services -l app=fiso-api
    
    echo ""
    echo "Ingress:"
    kubectl get ingress fiso-ingress
    
    # Get external IP
    EXTERNAL_IP=$(kubectl get service fiso-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
    echo ""
    echo "🌐 External Access:"
    echo "IP Address: $EXTERNAL_IP"
    echo "Health Check: http://$EXTERNAL_IP/health"
    echo "API Endpoint: http://$EXTERNAL_IP/api/v1"
    echo "Metrics: http://$EXTERNAL_IP/metrics"
}

# Main deployment function
main() {
    print_status "Starting FISO Kubernetes deployment..."
    
    # Pre-flight checks
    check_kubectl
    check_cluster
    
    # Deploy components
    deploy_secrets
    deploy_application
    deploy_monitoring
    deploy_ingress
    
    # Show status
    get_status
    
    print_success "🎉 FISO deployment completed successfully!"
    print_status "Access your FISO API at the external IP shown above"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "status")
        check_kubectl
        check_cluster
        get_status
        ;;
    "cleanup")
        print_warning "Cleaning up FISO deployment..."
        kubectl delete -f fiso-ingress.yaml --ignore-not-found=true
        kubectl delete -f fiso-monitoring.yaml --ignore-not-found=true
        kubectl delete -f fiso-deployment.yaml --ignore-not-found=true
        kubectl delete -f fiso-secrets.yaml --ignore-not-found=true
        print_success "Cleanup completed"
        ;;
    "help")
        echo "FISO Kubernetes Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy FISO to Kubernetes (default)"
        echo "  status   - Show deployment status"
        echo "  cleanup  - Remove FISO deployment"
        echo "  help     - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
