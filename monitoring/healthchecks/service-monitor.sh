#!/bin/bash
# Service Monitor Script for CostWatch
# Monitors Kubernetes pods, checks service health, and sends alerts on failures

set -e

# Configuration
NAMESPACE="${NAMESPACE:-costwatch}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
ALERT_THRESHOLD="${ALERT_THRESHOLD:-3}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    error "kubectl not found. Please install kubectl."
    exit 1
fi

# Send Slack alert
send_slack_alert() {
    local message="$1"
    local severity="${2:-warning}"

    if [ -z "$SLACK_WEBHOOK" ]; then
        warning "SLACK_WEBHOOK_URL not set, skipping alert"
        return
    fi

    local color="warning"
    if [ "$severity" == "critical" ]; then
        color="danger"
    elif [ "$severity" == "info" ]; then
        color="good"
    fi

    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{
            \"attachments\": [{
                \"color\": \"$color\",
                \"title\": \"CostWatch Alert\",
                \"text\": \"$message\",
                \"footer\": \"CostWatch Service Monitor\",
                \"ts\": $(date +%s)
            }]
        }" \
        2>/dev/null || warning "Failed to send Slack alert"
}

# Check pod health
check_pod_health() {
    local pod_name="$1"

    # Get pod status
    local status=$(kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")

    # Get restart count
    local restarts=$(kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || echo "0")

    # Check if pod is ready
    local ready=$(kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")

    echo "$status|$ready|$restarts"
}

# Check all services
check_all_services() {
    local failures=0

    log "Checking CostWatch services in namespace: $NAMESPACE"
    echo "=================================================="

    # Get all pods
    local pods=$(kubectl get pods -n "$NAMESPACE" \
        -l app -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

    if [ -z "$pods" ]; then
        error "No pods found in namespace $NAMESPACE"
        return 1
    fi

    for pod in $pods; do
        local health=$(check_pod_health "$pod")
        local status=$(echo "$health" | cut -d'|' -f1)
        local ready=$(echo "$health" | cut -d'|' -f2)
        local restarts=$(echo "$health" | cut -d'|' -f3)

        if [ "$status" != "Running" ] || [ "$ready" != "True" ]; then
            error "Pod $pod is unhealthy (Status: $status, Ready: $ready, Restarts: $restarts)"
            send_slack_alert "Pod $pod is unhealthy\nStatus: $status\nReady: $ready\nRestarts: $restarts" "critical"
            ((failures++))
        elif [ "$restarts" -ge "$ALERT_THRESHOLD" ]; then
            warning "Pod $pod has high restart count: $restarts"
            send_slack_alert "Pod $pod has restarted $restarts times" "warning"
        else
            success "Pod $pod is healthy (Restarts: $restarts)"
        fi
    done

    echo "=================================================="
    log "Health check complete. Failures: $failures"

    return $failures
}

# Check service endpoints
check_service_endpoints() {
    log "Checking service endpoints..."

    local services=("api-gateway" "cost-analyzer" "resource-scanner" "analytics-engine" "alert-manager")
    local failures=0

    for service in "${services[@]}"; do
        local svc_ip=$(kubectl get svc "$service" -n "$NAMESPACE" \
            -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

        if [ -z "$svc_ip" ]; then
            error "Service $service not found"
            ((failures++))
            continue
        fi

        # Get service port
        local port=$(kubectl get svc "$service" -n "$NAMESPACE" \
            -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8000")

        # Check health endpoint
        if kubectl run -i --rm --restart=Never curl-test \
            --image=curlimages/curl:latest -n "$NAMESPACE" \
            -- curl -s -f "http://$svc_ip:$port/health" &>/dev/null; then
            success "Service $service endpoint is healthy"
        else
            error "Service $service endpoint failed health check"
            send_slack_alert "Service $service health endpoint is failing" "critical"
            ((failures++))
        fi
    done

    return $failures
}

# Main monitoring loop
monitor_loop() {
    log "Starting continuous monitoring (interval: ${CHECK_INTERVAL}s)"

    while true; do
        check_all_services
        local exit_code=$?

        if [ $exit_code -eq 0 ]; then
            log "All services healthy"
        else
            error "$exit_code service(s) unhealthy"
        fi

        log "Waiting ${CHECK_INTERVAL}s before next check..."
        sleep "$CHECK_INTERVAL"
    done
}

# Main function
main() {
    case "${1:-check}" in
        check)
            check_all_services
            ;;
        endpoints)
            check_service_endpoints
            ;;
        monitor)
            monitor_loop
            ;;
        *)
            echo "Usage: $0 {check|endpoints|monitor}"
            echo "  check     - Run single health check"
            echo "  endpoints - Check service endpoints"
            echo "  monitor   - Run continuous monitoring"
            exit 1
            ;;
    esac
}

main "$@"
