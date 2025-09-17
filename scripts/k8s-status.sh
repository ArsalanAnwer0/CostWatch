#!/bin/bash

# CostWatch Kubernetes Status Script

NAMESPACE=${1:-costwatch}

echo "CostWatch Kubernetes Status"
echo "=========================="

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "Namespace '$NAMESPACE' does not exist"
    exit 1
fi

echo "Pods:"
kubectl get pods -n $NAMESPACE

echo -e "\nServices:"
kubectl get services -n $NAMESPACE

echo -e "\nDeployments:"
kubectl get deployments -n $NAMESPACE

echo -e "\nHPA Status:"
kubectl get hpa -n $NAMESPACE

echo -e "\nPod Resource Usage:"
kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics server not available"

echo -e "\nService Endpoints:"
kubectl get endpoints -n $NAMESPACE