# CostWatch API Examples

Quick reference for testing CostWatch API endpoints.

## Health Checks

Check if all services are running:

```bash
# Resource Scanner
curl http://localhost:8000/health

# Cost Analyzer
curl http://localhost:8001/health

# API Gateway
curl http://localhost:8002/health

# Analytics Engine
curl http://localhost:8003/health

# Alert Manager
curl http://localhost:8004/health
```

## Resource Scanner (Port 8000)

### Scan all AWS resources

```bash
curl -X POST http://localhost:8000/scan/all \
  -H "Content-Type: application/json" \
  -d '{
    "regions": ["us-west-2"],
    "include_costs": true
  }'
```

### Scan EC2 instances only

```bash
curl -X POST http://localhost:8000/scan/ec2 \
  -H "Content-Type: application/json" \
  -d '{
    "region": "us-west-2",
    "include_costs": true
  }'
```

### Get optimization recommendations

```bash
curl http://localhost:8000/optimize/ec2
```

## Cost Analyzer (Port 8001)

### Analyze costs for a period

```bash
curl -X POST http://localhost:8001/analyze/costs \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123456789012",
    "start_date": "2025-01-01",
    "end_date": "2025-01-15"
  }'
```

### Get optimization recommendations

```bash
curl -X POST http://localhost:8001/optimize/resources \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123456789012",
    "resource_types": ["ec2", "rds"]
  }'
```

### Analyze cost trends

```bash
curl -X POST http://localhost:8001/analyze/trends \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123456789012",
    "days": 30
  }'
```

## Analytics Engine (Port 8003)

### Analyze cost trends

```bash
curl -X POST http://localhost:8003/analytics/trends \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "000000000000",
    "start_date": "2025-01-01",
    "end_date": "2025-01-15",
    "metrics": ["total_cost", "daily_cost"]
  }'
```

### Generate cost predictions

```bash
curl -X POST http://localhost:8003/analytics/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "000000000000",
    "prediction_type": "cost_forecast",
    "time_horizon": 30
  }'
```

### Get dashboard data

```bash
curl "http://localhost:8003/analytics/dashboard/000000000000?period=last_30_days&include_forecasts=true"
```

### Detect cost anomalies

```bash
curl "http://localhost:8003/analytics/anomalies/000000000000?days=30&sensitivity=medium"
```

## Alert Manager (Port 8004)

### Send an alert

```bash
curl -X POST http://localhost:8004/alerts/send \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "cost_threshold",
    "severity": "high",
    "message": "Monthly cost exceeded threshold",
    "account_id": "000000000000",
    "metadata": {
      "threshold": 1000,
      "current_cost": 1250
    }
  }'
```

### Create alert rule

```bash
curl -X POST http://localhost:8004/alerts/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Budget Alert",
    "condition": "cost_exceeds",
    "threshold": 5000,
    "account_id": "000000000000",
    "notification_channels": ["sns", "email"]
  }'
```

### Check for cost alerts

```bash
curl -X POST http://localhost:8004/alerts/check \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "000000000000"
  }'
```

### Start cost monitoring

```bash
curl -X POST http://localhost:8004/alerts/monitor \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "000000000000",
    "interval_minutes": 60
  }'
```

## Using with jq for pretty output

Install jq for better JSON formatting:

```bash
# macOS
brew install jq

# Ubuntu/Debian
apt-get install jq
```

Then pipe your curl commands:

```bash
curl -s http://localhost:8000/health | jq '.'
```

## Testing with the health check script

Use our provided script to test all services at once:

```bash
./scripts/test-health.sh
```

## Common Issues

### Service not responding
- Check if containers are running: `docker-compose ps`
- View logs: `docker-compose logs <service-name>`
- Restart service: `docker-compose restart <service-name>`

### Connection refused
- Make sure services have finished starting (can take 30-60 seconds)
- Check Docker is running: `docker ps`
- Verify ports aren't blocked by firewall

### 500 Internal Server Error
- Check service logs: `docker-compose logs -f <service-name>`
- Verify AWS credentials are set (or use mock values)
- Ensure database is healthy: `docker-compose ps postgres`
