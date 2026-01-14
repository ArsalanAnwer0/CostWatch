# Troubleshooting Guide

Common issues and solutions for CostWatch deployment and operation.

## Table of Contents

- [Service Issues](#service-issues)
- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [Kubernetes Issues](#kubernetes-issues)
- [AWS Integration Issues](#aws-integration-issues)
- [Performance Issues](#performance-issues)
- [Monitoring Issues](#monitoring-issues)

---

## Service Issues

### Service Won't Start

**Symptom**: Service crashes immediately after starting

```bash
# Check logs
kubectl logs -n costwatch deployment/api-gateway --tail=100

# Common causes:
```

**Solution 1: Missing Environment Variables**
```bash
# Verify all required env vars are set
kubectl get secret costwatch-secrets -n costwatch -o yaml
kubectl describe configmap costwatch-config -n costwatch

# Check service startup logs for "environment variable required" errors
```

**Solution 2: Port Already in Use**
```bash
# Check if port is already bound
lsof -i :8002  # Replace with your service port

# Kill conflicting process or change port
```

**Solution 3: Database Connection Failed**
```bash
# Test database connectivity
psql -h localhost -U costwatch_user -d costwatch_dev

# Check connection string format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database
```

### Health Check Failures

**Symptom**: Kubernetes keeps restarting pods

```bash
# Check probe configuration
kubectl describe pod -n costwatch api-gateway-xxx

# Look for probe failure events
Events:
  Liveness probe failed: HTTP probe failed with statuscode: 500
```

**Solution**:
```yaml
# Increase timeout and failure threshold
livenessProbe:
  httpGet:
    path: /health
    port: 8002
  initialDelaySeconds: 30  # Increase this
  periodSeconds: 10
  failureThreshold: 5      # Increase this
  timeoutSeconds: 5
```

### Service Returns 500 Errors

**Symptom**: All requests return Internal Server Error

**Debug Steps**:
```bash
# 1. Check service logs
kubectl logs -n costwatch deployment/api-gateway --tail=100 | grep ERROR

# 2. Check for Python exceptions
kubectl logs -n costwatch deployment/api-gateway | grep Traceback -A 20

# 3. Enable debug logging
kubectl set env deployment/api-gateway LOG_LEVEL=DEBUG -n costwatch
```

**Common Causes**:
- Missing database migration
- Incorrect database schema
- Missing required secrets
- Unhandled exception in code

---

## Database Issues

### Connection Pool Exhausted

**Symptom**: `FATAL: sorry, too many clients already`

**Solution**:
```python
# Increase pool size in database.py
pool = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Increase from 10
    max_overflow=40,        # Increase from 20
    pool_timeout=30,
    pool_recycle=3600
)
```

```sql
-- Or increase PostgreSQL max_connections
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

### Slow Queries

**Symptom**: Requests timeout or take >5 seconds

**Debug**:
```sql
-- Enable query logging
ALTER DATABASE costwatch SET log_statement = 'all';
ALTER DATABASE costwatch SET log_min_duration_statement = 1000;  -- Log queries >1s

-- Find slow queries
SELECT
  calls,
  total_exec_time,
  mean_exec_time,
  query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solution**:
```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_cost_data_org_date
ON cost_data(organization_id, cost_date DESC);

-- Vacuum and analyze
VACUUM ANALYZE cost_data;
```

### Migration Failures

**Symptom**: Database migration fails partway through

**Recovery**:
```bash
# 1. Check current schema version
psql -d costwatch_prod -c "SELECT * FROM alembic_version;"

# 2. Manually rollback failed migration
psql -d costwatch_prod -f database/migrations/rollback_003.sql

# 3. Fix the migration script and retry
alembic upgrade head
```

---

## Authentication Issues

### JWT Token Invalid

**Symptom**: `401 Unauthorized` on all authenticated requests

**Debug**:
```python
# Verify JWT secret matches
import os
print(os.getenv("JWT_SECRET_KEY"))

# Test token generation
from jose import jwt
token = jwt.encode({"sub": "test"}, SECRET_KEY, algorithm="HS256")
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
print(decoded)
```

**Solution**:
```bash
# Ensure JWT_SECRET_KEY is consistent across all services
kubectl get secret costwatch-secrets -n costwatch -o jsonpath='{.data.JWT_SECRET_KEY}' | base64 -d

# Regenerate secret if corrupted
openssl rand -base64 32
kubectl create secret generic costwatch-secrets \
  --from-literal=JWT_SECRET_KEY="new-secret" \
  -n costwatch --dry-run=client -o yaml | kubectl apply -f -

# Restart all services
kubectl rollout restart deployment -n costwatch
```

### Password Hash Verification Fails

**Symptom**: Users can't login even with correct password

**Debug**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test hashing
password = "testpassword"
hashed = pwd_context.hash(password)
print(f"Hash: {hashed}")

# Verify
is_valid = pwd_context.verify(password, hashed)
print(f"Valid: {is_valid}")
```

**Solution**:
```python
# Ensure bcrypt is installed
pip install bcrypt passlib

# Check password was hashed correctly
# Bcrypt hashes start with $2b$
SELECT username, password_hash FROM users LIMIT 1;
# Should look like: $2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Kubernetes Issues

### Pods in CrashLoopBackOff

**Symptom**: Pod keeps restarting

```bash
# Check pod status
kubectl get pods -n costwatch

# Check events
kubectl describe pod api-gateway-xxx -n costwatch

# Check logs from previous container
kubectl logs api-gateway-xxx -n costwatch --previous
```

**Common Causes**:

1. **Missing ConfigMap/Secret**:
```bash
kubectl get configmap costwatch-config -n costwatch
kubectl get secret costwatch-secrets -n costwatch
```

2. **Image Pull Error**:
```bash
# Check image exists
docker pull costwatch/api-gateway:latest

# Check image pull secrets
kubectl get secret costwatch-registry-secret -n costwatch
```

3. **Resource Limits Too Low**:
```yaml
resources:
  requests:
    memory: "512Mi"  # Increase if OOMKilled
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Services Not Accessible

**Symptom**: Can't reach service from outside cluster

**Debug**:
```bash
# Check service exists
kubectl get svc -n costwatch

# Check endpoints are ready
kubectl get endpoints api-gateway-service -n costwatch

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://api-gateway-service.costwatch.svc.cluster.local:8002/health
```

**Solution**:
```bash
# Port forward for debugging
kubectl port-forward -n costwatch svc/api-gateway-service 8002:8002

# Check Ingress configuration
kubectl get ingress -n costwatch
kubectl describe ingress costwatch-ingress -n costwatch
```

### Persistent Volume Issues

**Symptom**: Pod can't mount volume

```bash
# Check PV and PVC status
kubectl get pv,pvc -n costwatch

# Check events
kubectl describe pvc postgres-pvc -n costwatch
```

**Solution**:
```bash
# Delete and recreate PVC (WARNING: loses data)
kubectl delete pvc postgres-pvc -n costwatch
kubectl apply -f k8s/storage/postgres-pvc.yaml

# Or increase volume size
kubectl patch pvc postgres-pvc -n costwatch \
  -p '{"spec":{"resources":{"requests":{"storage":"50Gi"}}}}'
```

---

## AWS Integration Issues

### Cost Explorer API Errors

**Symptom**: `AccessDeniedException` when fetching cost data

**Debug**:
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Cost Explorer access
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

**Solution**:
```json
// Add required IAM policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetDimensionValues"
      ],
      "Resource": "*"
    }
  ]
}
```

### CloudWatch Metrics Not Available

**Symptom**: Resource utilization always returns null

**Debug**:
```python
import boto3

cloudwatch = boto3.client('cloudwatch')
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId', 'Value': 'i-xxxxx'}],
    StartTime=datetime.now() - timedelta(hours=1),
    EndTime=datetime.now(),
    Period=300,
    Statistics=['Average']
)
print(response)
```

**Solution**:
```json
// Add CloudWatch read permissions
{
  "Effect": "Allow",
  "Action": [
    "cloudwatch:GetMetricStatistics",
    "cloudwatch:ListMetrics"
  ],
  "Resource": "*"
}
```

### IAM Role Not Assumed

**Symptom**: Getting credentials error despite IRSA configured

**Debug**:
```bash
# Check service account annotation
kubectl get sa costwatch-sa -n costwatch -o yaml

# Should have:
# eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/costwatch-role

# Check pod environment
kubectl exec -n costwatch api-gateway-xxx -- env | grep AWS
```

**Solution**:
```bash
# Recreate service account with correct annotation
kubectl annotate sa costwatch-sa -n costwatch \
  eks.amazonaws.com/role-arn=arn:aws:iam::ACCOUNT:role/ROLE_NAME

# Restart pods to pick up new service account
kubectl rollout restart deployment -n costwatch
```

---

## Performance Issues

### High Memory Usage

**Symptom**: Pods getting OOMKilled

**Debug**:
```bash
# Check memory usage
kubectl top pods -n costwatch

# Get detailed metrics
kubectl describe node
```

**Solution**:
```python
# Add memory profiling
import tracemalloc

tracemalloc.start()
# Your code here
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

```yaml
# Increase memory limits
resources:
  limits:
    memory: "2Gi"  # Increase from 1Gi
```

### High CPU Usage

**Symptom**: Service slow, CPU at 100%

**Debug**:
```bash
# Check CPU usage
kubectl top pods -n costwatch

# Profile Python code
pip install py-spy
py-spy top --pid <PID>
```

**Solution**:
```python
# Add caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_monthly_costs(org_id: UUID, month: date):
    # Expensive calculation
    return result

# Or use Redis cache
import redis
cache = redis.Redis(host='redis', port=6379)

def get_costs(org_id):
    key = f"costs:{org_id}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

    result = expensive_calculation()
    cache.setex(key, 3600, json.dumps(result))  # Cache for 1 hour
    return result
```

### Slow API Responses

**Symptom**: Requests taking >2 seconds

**Debug**:
```python
# Add timing middleware
import time
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Process-Time"] = str(duration)
        print(f"{request.url.path}: {duration:.3f}s")
        return response

app.add_middleware(TimingMiddleware)
```

**Solutions**:
- Add database indexes
- Implement caching
- Use async/await properly
- Reduce N+1 queries
- Add pagination

---

## Monitoring Issues

### Prometheus Not Scraping Metrics

**Symptom**: No metrics in Grafana dashboards

**Debug**:
```bash
# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090/targets

# Check service annotations
kubectl get svc api-gateway-service -n costwatch -o yaml
```

**Solution**:
```yaml
# Add Prometheus annotations to service
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8002"
    prometheus.io/path: "/metrics"
```

### Grafana Dashboard Shows No Data

**Symptom**: Dashboard panels empty

**Debug**:
```bash
# Check data source connection in Grafana
# Settings > Data Sources > PostgreSQL > Test

# Test query directly
psql -d costwatch_prod -c "SELECT COUNT(*) FROM cost_data;"
```

**Solution**:
```sql
-- Ensure data exists
SELECT * FROM cost_data ORDER BY created_at DESC LIMIT 10;

-- Check time range in Grafana matches data
SELECT MIN(cost_date), MAX(cost_date) FROM cost_data;
```

### Alerts Not Firing

**Symptom**: No alerts despite issues

**Debug**:
```bash
# Check AlertManager configuration
kubectl logs -n monitoring deployment/alertmanager

# Check Prometheus rules
kubectl get prometheusrule -n monitoring

# Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts -d '[{
  "labels": {"alertname": "test"},
  "annotations": {"summary": "test alert"}
}]'
```

**Solution**:
```yaml
# Verify alert rule syntax
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: costwatch-alerts
spec:
  groups:
  - name: services
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"
```

---

## Getting More Help

If issues persist:

1. **Check Logs**: Always start with service logs
2. **Search Issues**: Check GitHub issues for similar problems
3. **Ask Community**: Post in GitHub Discussions
4. **Contact Support**: Email support@costwatch.com

### Useful Commands

```bash
# Get all resources in namespace
kubectl get all -n costwatch

# Describe all pods
kubectl describe pods -n costwatch

# Stream logs from all pods
kubectl logs -f -n costwatch -l app=api-gateway

# Execute command in pod
kubectl exec -it -n costwatch api-gateway-xxx -- /bin/bash

# Debug networking
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- /bin/bash
```

---

## FAQ

**Q: How do I reset the database?**
```bash
psql -d costwatch_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -d costwatch_dev -f database/schemas/01_init.sql
```

**Q: How do I force pull latest Docker images?**
```bash
kubectl rollout restart deployment -n costwatch
kubectl set image deployment/api-gateway api-gateway=costwatch/api-gateway:latest -n costwatch
```

**Q: How do I enable debug mode?**
```bash
kubectl set env deployment/api-gateway LOG_LEVEL=DEBUG -n costwatch
```

**Q: How do I backup the database?**
```bash
pg_dump -h localhost -U postgres costwatch_prod > backup_$(date +%Y%m%d).sql
```

**Q: How do I scale a service?**
```bash
kubectl scale deployment api-gateway --replicas=3 -n costwatch
```

---

For more information, see:
- [Architecture Documentation](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Security Guide](./SECURITY.md)
