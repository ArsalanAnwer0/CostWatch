#!/bin/bash

# CostWatch Deployment Script
# Deploys CostWatch services to Kubernetes cluster

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NAMESPACE="costwatch"
ENVIRONMENT="${1:-dev}"
VERSION="${2:-latest}"
DRY_RUN="${DRY_RUN:-false}"

SERVICES=("api-gateway" "cost-analyzer" "resource-scanner" "analytics-engine" "alert-manager")

log() { echo -e "${1}${2}\033[0m"; }
success() { log "\033[0;32m" "✓ $1"; }
warn() { log "\033[1;33m" "⚠ $1"; }
error_exit() { echo -e "\033[0;31mERROR: $1\033[0m"; exit 1; }

# Validate environment
case "$ENVIRONMENT" in
    dev|staging|prod) success "Environment: $ENVIRONMENT" ;;
    *) error_exit "Invalid environment: $ENVIRONMENT" ;;
esac

# Check prerequisites
command -v kubectl &> /dev/null || error_exit "kubectl not installed"
command -v docker &> /dev/null || error_exit "docker not installed"

log "$GREEN" "Deploying CostWatch to $ENVIRONMENT..."

# Create namespace
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy base resources
kubectl apply -f "$PROJECT_ROOT/k8s/base/configmaps/" -n "$NAMESPACE"

# Deploy services
for service in "${SERVICES[@]}"; do
    log "$YELLOW" "Deploying $service..."
    kubectl apply -f "$PROJECT_ROOT/k8s/services/$service/" -n "$NAMESPACE"
done

success "Deployment complete!"
