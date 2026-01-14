# Monitoring & Observability Guide

Comprehensive monitoring setup for Cost Watch using Prometheus, Grafana, and alerting.

## Table of Contents

- [Overview](#overview)
- [Prometheus Setup](#prometheus-setup)
- [Grafana Configuration](#grafana-configuration)
- [Alert Rules](#alert-rules)
- [Metrics Reference](#metrics-reference)
- [Dashboards](#dashboards)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)

---

## Overview

CostWatch uses a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboarding
- **AlertManager**: Alert routing and notification
- **Exporters**: PostgreSQL, Redis, NGINX metrics

### Architecture

```
┌─────────────────┐
│  Microservices  │ ─── /metrics ──> ┌────────────┐
│  (5 services)   │                  │ Prometheus │
└─────────────────┘                  └──────┬─────┘
                                             │
┌─────────────────┐                          │
│   PostgreSQL    │ ─── Exporter ────────────┤
└─────────────────┘                          │
                                             │
┌─────────────────┐                          │
│     Redis       │ ─── Exporter ────────────┤
└─────────────────┘                          │
                                             │
┌─────────────────┐                          │
│ NGINX Ingress   │ ─── Metrics ─────────────┤
└─────────────────┘                          │
                                             ▼
                                       ┌──────────┐
                                       │ Grafana  │
                                       └──────────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │ Alert Mgr   │
                                      └─────────────┘
```

---

## Prometheus Setup

### Installation

#### Using Docker Compose (Development)

```bash
docker-compose up -d prometheus grafana
```

#### Using Kubernetes (Production)

```bash
# Deploy Prometheus
kubectl apply -f k8s/monitoring/prometheus/

# Verify deployment
kubectl get pods -n monitoring
kubectl logs -f -n monitoring prometheus-0
```

### Configuration

Prometheus configuration is located at `monitoring/prometheus/prometheus.yml`.

#### Key Configuration Sections

**Global Settings**
```yaml
global:
  scrape_interval: 15s      # How often to scrape targets
  evaluation_interval: 15s   # How often to evaluate rules
  external_labels:
    cluster: 'costwatch-prod'
    environment: 'production'
```

**Service Discovery**

CostWatch uses both static and Kubernetes service discovery:

```yaml
scrape_configs:
  # Static configuration for services
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Kubernetes pod discovery
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - costwatch
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Scrape Targets

| Job Name | Target | Port | Path | Interval |
|----------|--------|------|------|----------|
| api-gateway | api-gateway-service | 8002 | /metrics | 10s |
| cost-analyzer | cost-analyzer-service | 8001 | /metrics | 15s |
| resource-scanner | resource-scanner-service | 8000 | /metrics | 30s |
| analytics-engine | analytics-engine-service | 8003 | /metrics | 20s |
| alert-manager | alert-manager-service | 8004 | /metrics | 10s |
| postgresql | postgres-exporter | 9187 | /metrics | 15s |
| redis | redis-exporter | 9121 | /metrics | 15s |
| nginx-ingress | nginx-ingress-controller | 10254 | /metrics | 10s |

### Accessing Prometheus

#### Local Development
```bash
# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Access UI
open http://localhost:9090
```

#### Production
Access via ingress: `https://prometheus.costwatch.com`

### Common PromQL Queries

#### Request Rate
```promql
# Requests per second per service
rate(http_requests_total[5m])

# Request rate by endpoint
sum(rate(http_requests_total[5m])) by (endpoint)
```

#### Error Rate
```promql
# Error rate percentage
100 * sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# Errors by service
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
```

#### Latency
```promql
# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average latency by endpoint
avg(rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])) by (endpoint)
```

#### Database Metrics
```promql
# Active database connections
pg_stat_database_numbackends

# Slow queries
rate(pg_stat_statements_calls{queryid=~".*"}[5m]) > 1

# Database size
pg_database_size_bytes / 1024 / 1024 / 1024
```

#### Resource Utilization
```promql
# CPU usage by service
rate(process_cpu_seconds_total[5m]) * 100

# Memory usage
process_resident_memory_bytes / 1024 / 1024
```

---

## Grafana Configuration

### Installation

Grafana is included in the monitoring stack.

```bash
# Deploy Grafana
kubectl apply -f k8s/monitoring/grafana/

# Get admin password
kubectl get secret -n monitoring grafana-admin -o jsonpath='{.data.password}' | base64 -d
```

### Accessing Grafana

#### Local Development
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
open http://localhost:3000
```

**Default Credentials:**
- Username: `admin`
- Password: Check secrets or set via environment variable

#### Production
Access via ingress: `https://grafana.costwatch.com`

### Data Sources

#### PostgreSQL Data Source

Configuration: `monitoring/grafana/datasources/postgres-datasource.json`

```json
{
  "name": "CostWatch PostgreSQL",
  "type": "postgres",
  "url": "postgres-service.costwatch.svc.cluster.local:5432",
  "database": "costwatch_prod",
  "user": "${POSTGRES_USER}",
  "secureJsonData": {
    "password": "${POSTGRES_PASSWORD}"
  },
  "jsonData": {
    "sslmode": "require",
    "postgresVersion": 1500
  }
}
```

**To add via UI:**
1. Configuration → Data Sources → Add data source
2. Select PostgreSQL
3. Fill in connection details
4. Save & Test

#### Prometheus Data Source

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus-service.monitoring.svc.cluster.local:9090",
  "access": "proxy",
  "isDefault": true
}
```

### Dashboards

CostWatch includes pre-built dashboards:

| Dashboard | File | Purpose |
|-----------|------|---------|
| Cost Analysis | `cost-analysis.json` | Cost trends, forecasts, optimization |
| Service Overview | `service-overview.json` | Service health, request rates, latency |
| Database Performance | `database-performance.json` | Query performance, connections, locks |
| Application Performance | `apm-dashboard.json` | APM metrics, traces, errors |
| Infrastructure | `infrastructure.json` | CPU, memory, disk, network |
| Alerts | `alerts-dashboard.json` | Active alerts, alert history |

#### Importing Dashboards

**Via UI:**
1. + icon → Import
2. Upload JSON file from `monitoring/grafana/dashboards/`
3. Select Prometheus data source
4. Import

**Via ConfigMap:**
```bash
kubectl create configmap grafana-dashboards \
  --from-file=monitoring/grafana/dashboards/ \
  -n monitoring
```

#### Creating Custom Dashboards

**Example Panel: Request Rate**

```json
{
  "title": "Request Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total[5m])) by (service)",
      "legendFormat": "{{service}}"
    }
  ],
  "type": "graph"
}
```

### Dashboard Best Practices

1. **Use Template Variables**: Makes dashboards reusable across environments
   ```
   $environment, $service, $pod
   ```

2. **Set Appropriate Time Ranges**: Default to Last 1 hour with auto-refresh

3. **Group Related Metrics**: Use rows to organize panels logically

4. **Add Descriptions**: Use panel descriptions to explain metrics

5. **Configure Alerts**: Set up alert thresholds in panel settings

---

## Alert Rules

Alert rules are defined in `monitoring/prometheus/alert_rules.yml`.

### High-Level Alerts

#### Service Down Alert
```yaml
- alert: ServiceDown
  expr: up == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Service {{ $labels.job }} is down"
    description: "{{ $labels.job }} has been down for more than 1 minute"
```

#### High Error Rate
```yaml
- alert: HighErrorRate
  expr: |
    (sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
    / sum(rate(http_requests_total[5m])) by (service)) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate on {{ $labels.service }}"
    description: "Error rate is {{ $value | humanizePercentage }}"
```

#### High Latency
```yaml
- alert: HighLatency
  expr: |
    histogram_quantile(0.95,
      sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
    ) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High latency on {{ $labels.service }}"
    description: "95th percentile latency is {{ $value }}s"
```

### Database Alerts

#### High Database Connections
```yaml
- alert: HighDatabaseConnections
  expr: pg_stat_database_numbackends > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High number of database connections"
    description: "{{ $value }} active connections"
```

#### Slow Queries
```yaml
- alert: SlowQueries
  expr: |
    pg_stat_statements_mean_exec_time_seconds > 5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Slow database queries detected"
    description: "Average query time is {{ $value }}s"
```

### Cost-Specific Alerts

#### Cost Threshold Exceeded
```yaml
- alert: CostThresholdExceeded
  expr: |
    sum(aws_cost_monthly_total) > 10000
  for: 1h
  labels:
    severity: high
  annotations:
    summary: "Monthly AWS cost exceeded threshold"
    description: "Current monthly cost: ${{ $value }}"
```

#### Anomalous Cost Spike
```yaml
- alert: AnomalousCostSpike
  expr: |
    (aws_cost_daily_total - avg_over_time(aws_cost_daily_total[7d]))
    / avg_over_time(aws_cost_daily_total[7d]) > 0.5
  for: 30m
  labels:
    severity: high
  annotations:
    summary: "Unusual cost spike detected"
    description: "Daily cost 50% higher than 7-day average"
```

### Notification Channels

Configure AlertManager to send notifications via:

- **Email**: SMTP configuration
- **Slack**: Webhook integration
- **PagerDuty**: API integration
- **Webhook**: Custom HTTP endpoints

**AlertManager Configuration:**
```yaml
route:
  receiver: 'default'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'alerts@costwatch.com'
        from: 'alertmanager@costwatch.com'
        smarthost: 'smtp.gmail.com:587'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

---

## Metrics Reference

### Application Metrics

All CostWatch services expose metrics on `/metrics` endpoint.

#### HTTP Metrics
```
# Request counter
http_requests_total{method, endpoint, status}

# Request duration histogram
http_request_duration_seconds{method, endpoint}

# Request size
http_request_size_bytes{method, endpoint}

# Response size
http_response_size_bytes{method, endpoint}
```

#### Business Metrics
```
# Cost analysis metrics
costwatch_cost_total{organization_id, service}
costwatch_resources_scanned_total{service, region}
costwatch_alerts_triggered_total{alert_type, severity}
costwatch_optimization_savings_potential{resource_type}

# Report generation
costwatch_reports_generated_total{report_type}
costwatch_report_generation_duration_seconds{report_type}
```

#### System Metrics
```
# Process metrics
process_cpu_seconds_total
process_resident_memory_bytes
process_open_fds
process_max_fds

# Python-specific
python_gc_objects_collected_total
python_info{version}
```

### Database Metrics

Exported by `postgres_exporter`:

```
# Connections
pg_stat_database_numbackends{datname}
pg_stat_activity_count{state}

# Transactions
pg_stat_database_xact_commit{datname}
pg_stat_database_xact_rollback{datname}

# Query performance
pg_stat_statements_calls{queryid}
pg_stat_statements_mean_exec_time_seconds{queryid}

# Locks
pg_locks_count{mode}

# Replication
pg_stat_replication_lag_bytes
```

### Infrastructure Metrics

#### Redis Metrics
```
redis_connected_clients
redis_used_memory_bytes
redis_commands_processed_total
redis_keyspace_hits_total
redis_keyspace_misses_total
```

#### NGINX Metrics
```
nginx_ingress_controller_requests
nginx_ingress_controller_request_duration_seconds
nginx_ingress_controller_response_duration_seconds
nginx_ingress_controller_ssl_expire_time_seconds
```

---

## Dashboards

### Cost Analysis Dashboard

**Panels:**
1. Total Monthly Cost (Single Stat)
2. Cost Trend (Time Series)
3. Cost by Service (Pie Chart)
4. Cost Forecast (Line Chart with prediction)
5. Optimization Opportunities (Table)
6. Cost Anomalies (Alert List)

**Queries:**
```promql
# Total cost
sum(aws_cost_monthly_total)

# Cost by service
sum(aws_cost_monthly_total) by (service)

# Cost trend
avg_over_time(aws_cost_daily_total[7d])
```

### Service Overview Dashboard

**Panels:**
1. Service Status (Stat)
2. Request Rate (Graph)
3. Error Rate (Graph)
4. Latency Percentiles (Graph)
5. Active Connections (Stat)
6. Recent Errors (Logs)

### Database Performance Dashboard

**Panels:**
1. Query Performance (Table)
2. Connection Pool Status (Graph)
3. Slow Query Log (Table)
4. Database Size (Stat)
5. Transaction Rate (Graph)
6. Lock Waits (Graph)

### Application Performance (APM) Dashboard

**Panels:**
1. Service Map (Node Graph)
2. Trace Spans (Timeline)
3. Error Traces (List)
4. Latency Heatmap (Heatmap)
5. Resource Utilization (Graph)

---

## Health Checks

### Automated Health Monitoring

#### Health Monitor Script

Location: `monitoring/healthchecks/health-monitor.py`

```python
#!/usr/bin/env python3
"""
Health monitoring script for CostWatch services.
Checks all service endpoints and reports status.
"""

import requests
import sys
from datetime import datetime

SERVICES = {
    "api-gateway": "http://api-gateway-service:8002/health",
    "cost-analyzer": "http://cost-analyzer-service:8001/health",
    "resource-scanner": "http://resource-scanner-service:8000/health",
    "analytics-engine": "http://analytics-engine-service:8003/health",
    "alert-manager": "http://alert-manager-service:8004/health",
}

def check_service(name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "service": name,
                "status": "healthy",
                "response_time": response.elapsed.total_seconds(),
                "details": data
            }
        else:
            return {
                "service": name,
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "service": name,
            "status": "unreachable",
            "error": str(e)
        }

def main():
    results = []
    for name, url in SERVICES.items():
        result = check_service(name, url)
        results.append(result)

    # Print results
    print(f"Health Check Report - {datetime.now().isoformat()}")
    print("=" * 60)

    for result in results:
        status_symbol = "✓" if result["status"] == "healthy" else "✗"
        print(f"{status_symbol} {result['service']}: {result['status']}")
        if "error" in result:
            print(f"  Error: {result['error']}")

    # Exit with error if any service is unhealthy
    unhealthy = [r for r in results if r["status"] != "healthy"]
    if unhealthy:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Run health checks:**
```bash
python monitoring/healthchecks/health-monitor.py
```

#### Service Monitor Script

Location: `monitoring/healthchecks/service-monitor.sh`

```bash
#!/bin/bash
# Monitor Kubernetes services and pods

NAMESPACE="costwatch"

echo "=== Pod Status ==="
kubectl get pods -n $NAMESPACE

echo -e "\n=== Service Status ==="
kubectl get svc -n $NAMESPACE

echo -e "\n=== Recent Events ==="
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

echo -e "\n=== Resource Usage ==="
kubectl top pods -n $NAMESPACE
```

### Manual Health Checks

#### Check Prometheus Targets
```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
```

#### Check Service Endpoints
```bash
# API Gateway
curl http://api-gateway-service:8002/health

# Cost Analyzer
curl http://cost-analyzer-service:8001/health

# Resource Scanner
curl http://resource-scanner-service:8000/health
```

#### Check Database Connectivity
```bash
psql -h postgres-service -U costwatch_user -d costwatch_prod -c "SELECT 1"
```

---

## Troubleshooting

### Prometheus Not Scraping Targets

**Symptoms:**
- Targets show as "DOWN" in Prometheus UI
- No metrics data in Grafana

**Debug:**
```bash
# Check Prometheus logs
kubectl logs -n monitoring prometheus-0

# Check target configuration
kubectl port-forward -n monitoring prometheus-0 9090:9090
# Visit http://localhost:9090/targets

# Test connectivity to service
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://api-gateway-service.costwatch:8002/metrics
```

**Solutions:**
1. Verify service is running and healthy
2. Check network policies allow Prometheus → service traffic
3. Verify metrics endpoint is accessible
4. Check Prometheus configuration syntax

### Grafana Showing No Data

**Symptoms:**
- Dashboards show "No Data"
- Queries return empty results

**Debug:**
```bash
# Check data source connection
# Grafana UI → Configuration → Data Sources → Test

# Test Prometheus query directly
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up'

# Check time range in Grafana matches data availability
```

**Solutions:**
1. Verify Prometheus is collecting data
2. Check time range selection in Grafana
3. Verify PromQL query syntax
4. Check data source configuration

### Alerts Not Firing

**Symptoms:**
- Expected alerts not triggering
- No notifications received

**Debug:**
```bash
# Check AlertManager status
kubectl logs -n monitoring alertmanager-0

# Check alert rules in Prometheus
# Visit http://localhost:9090/alerts

# Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts -d '[{
  "labels": {"alertname": "test", "severity": "warning"},
  "annotations": {"summary": "Test alert"}
}]'
```

**Solutions:**
1. Verify alert rule syntax
2. Check "for" duration hasn't elapsed
3. Verify AlertManager routing configuration
4. Check notification channel credentials

### High Cardinality Issues

**Symptoms:**
- Prometheus consuming excessive memory
- Slow query performance

**Debug:**
```bash
# Check series count
curl http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName'

# Identify high-cardinality metrics
curl http://localhost:9090/api/v1/label/__name__/values | \
  jq -r '.data[]' | \
  while read metric; do
    count=$(curl -s "http://localhost:9090/api/v1/query?query=count($metric)" | jq '.data.result[0].value[1]')
    echo "$metric: $count"
  done | sort -t: -k2 -rn | head -10
```

**Solutions:**
1. Reduce label cardinality (avoid IDs, timestamps in labels)
2. Increase retention period to spread data
3. Use recording rules for expensive queries
4. Implement relabeling to drop unnecessary labels

---

## Best Practices

### Metrics

1. **Use Standard Metric Types**: Counter, Gauge, Histogram, Summary
2. **Follow Naming Conventions**: `<namespace>_<name>_<unit>`
3. **Limit Label Cardinality**: Avoid high-cardinality labels (user IDs, timestamps)
4. **Add Help Text**: Include description for each metric
5. **Expose Internal State**: Instrument critical code paths

### Dashboards

1. **Start Simple**: Begin with key metrics, add detail iteratively
2. **Use Variables**: Make dashboards reusable across environments
3. **Set Appropriate Refresh**: Balance freshness vs load
4. **Document Panels**: Add descriptions explaining what metrics mean
5. **Create Folders**: Organize dashboards by team or component

### Alerts

1. **Alert on Symptoms, Not Causes**: Focus on user-facing issues
2. **Set Appropriate Thresholds**: Avoid alert fatigue
3. **Use "for" Duration**: Prevent flapping alerts
4. **Write Actionable Descriptions**: Include runbook links
5. **Route by Severity**: Critical → PagerDuty, Warning → Slack

### Performance

1. **Use Recording Rules**: Pre-compute expensive queries
2. **Limit Query Range**: Use appropriate time windows
3. **Optimize PromQL**: Use `rate()` over `irate()`, aggregate early
4. **Configure Retention**: Balance storage vs history needs
5. **Monitor Prometheus Itself**: Set up self-monitoring

---

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [CostWatch Architecture](./ARCHITECTURE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

## Support

For monitoring issues:
- Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review Prometheus/Grafana logs
- Contact: monitoring@costwatch.com
