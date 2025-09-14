#!/bin/bash

# Update kubeconfig for CostWatch EKS cluster

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-west-2}
PROJECT_NAME="costwatch"
CLUSTER_NAME="${PROJECT_NAME}-cluster-${ENVIRONMENT}"

echo "🔧 Updating kubeconfig for cluster: $CLUSTER_NAME"

# Update kubeconfig
aws eks update-kubeconfig \
    --region "$AWS_REGION" \
    --name "$CLUSTER_NAME"

if [ $? -eq 0 ]; then
    echo " Kubeconfig updated successfully"
    echo " Testing cluster connection..."
    
    if kubectl get nodes >/dev/null 2>&1; then
        echo " Successfully connected to cluster"
        kubectl get nodes
    else
        echo " Failed to connect to cluster"
        exit 1
    fi
else
    echo " Failed to update kubeconfig"
    exit 1
fi