#!/bin/bash

# CostWatch Simple Deployment Script
set -e

echo "Starting CostWatch deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl not found. Please install kubectl first."
    exit 1
fi

echo "Deploying to Kubernetes..."

# Create namespace
kubectl create namespace costwatch --dry-run=client -o yaml | kubectl apply -f -

# Apply all Kubernetes manifests
kubectl apply -f k8s/base/namespace/
kubectl apply -f k8s/base/configmaps/
kubectl apply -f k8s/base/secrets/
kubectl apply -f k8s/base/rbac/
kubectl apply -f k8s/services/
kubectl apply -f k8s/monitoring/

echo "Waiting for deployments..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n costwatch || echo "Some deployments may still be starting"

echo "Checking status..."
kubectl get pods -n costwatch
kubectl get services -n costwatch

echo "Deployment completed!"
echo "To check logs: kubectl logs -f deployment/api-gateway -n costwatch"