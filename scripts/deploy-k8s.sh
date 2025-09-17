#!/bin/bash

# CostWatch Kubernetes Deployment Script

set -e

NAMESPACE=${1:-costwatch}
ENVIRONMENT=${2:-dev}

echo "Deploying CostWatch to Kubernetes..."
echo "Namespace: $NAMESPACE"
echo "Environment: $ENVIRONMENT"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "Cannot connect to Kubernetes cluster"
    echo "Make sure your kubeconfig is properly configured"
    exit 1
fi

# Apply namespace first
echo "Creating namespace..."
kubectl apply -f k8s/base/namespace/costwatch-namespace.yaml

# Apply base configuration
echo "Applying base configuration..."
kubectl apply -f k8s/base/configmaps/
kubectl apply -f k8s/base/secrets/

# Apply network policies
echo "Applying network policies..."
kubectl apply -f k8s/base/network-policies.yaml

# Deploy services
echo "Deploying API Gateway..."
kubectl apply -f k8s/services/api-gateway/

echo "Deploying Resource Scanner..."
kubectl apply -f k8s/services/resource-scanner/

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/api-gateway -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/resource-scanner -n $NAMESPACE

# Display status
echo "Deployment Status:"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "CostWatch deployed successfully!"

# Get LoadBalancer IP if available
LB_IP=$(kubectl get service api-gateway-loadbalancer -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
if [ -n "$LB_IP" ]; then
    echo "API Gateway is accessible at: http://$LB_IP"
else
    echo "LoadBalancer IP is pending. Check with: kubectl get service api-gateway-loadbalancer -n $NAMESPACE"
fi