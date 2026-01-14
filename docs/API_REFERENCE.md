# CostWatch API Reference

Comprehensive API documentation for CostWatch microservices.

## Base URLs

| Environment | API Gateway Base URL |
|------------|---------------------|
| Development | `http://localhost:8002` |
| Staging | `https://api-staging.costwatch.com` |
| Production | `https://api.costwatch.com` |

## Authentication

All API endpoints (except `/auth/register` and `/auth/login`) require authentication via JWT bearer token.

### Obtaining a Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "organization_id": "uuid"
  }
}
```

### Using Authentication

Include the token in the `Authorization` header:

```http
GET /api/costs/monthly
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API Gateway Endpoints

Base service: **api-gateway** (Port 8002)

### Authentication

#### Register New User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "organization_name": "Acme Corp"
}
```

**Response: 201 Created**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newuser@example.com",
  "organization_id": "660e8400-e29b-41d4-a716-446655440000",
  "message": "User registered successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email format or weak password
- `409 Conflict`: Email already registered

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VySWQiLCJleHAiOjE3MDk5OTk5OTl9.signature",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

### Health Check

#### Service Health

```http
GET /health
```

**Response: 200 OK**
```json
{
  "status": "healthy",
  "service": "api-gateway",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "downstream_services": {
      "cost-analyzer": "healthy",
      "resource-scanner": "healthy",
      "analytics-engine": "healthy",
      "alert-manager": "healthy"
    }
  }
}
```

---

## Cost Analysis Endpoints

Proxied through API Gateway to **cost-analyzer** service (Port 8001)

### Get Monthly Costs

```http
GET /api/costs/monthly?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer {token}
```

**Query Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `granularity` (optional): `DAILY` | `MONTHLY` (default: `MONTHLY`)
- `group_by` (optional): `SERVICE` | `REGION` | `ACCOUNT`

**Response: 200 OK**
```json
{
  "organization_id": "660e8400-e29b-41d4-a716-446655440000",
  "period": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "total_cost": 125678.45,
  "currency": "USD",
  "breakdown": [
    {
      "date": "2024-01",
      "amount": 10234.56,
      "services": {
        "EC2": 4500.00,
        "RDS": 3200.00,
        "S3": 1534.56,
        "Other": 1000.00
      }
    }
  ]
}
```

### Get Cost Optimization Recommendations

```http
GET /api/costs/optimize
Authorization: Bearer {token}
```

**Query Parameters:**
- `service` (optional): Filter by AWS service (e.g., `EC2`, `RDS`, `S3`)
- `min_savings` (optional): Minimum potential savings in USD (default: 0)

**Response: 200 OK**
```json
{
  "recommendations": [
    {
      "id": "rec-001",
      "resource_id": "i-0123456789abcdef0",
      "resource_type": "EC2",
      "recommendation_type": "DOWNSIZE",
      "current_cost": 876.00,
      "estimated_savings": 438.00,
      "confidence": "HIGH",
      "details": {
        "current_instance_type": "m5.2xlarge",
        "recommended_instance_type": "m5.xlarge",
        "avg_cpu_utilization": 15.2,
        "avg_memory_utilization": 22.3
      },
      "action": "Downsize instance from m5.2xlarge to m5.xlarge",
      "impact": "LOW"
    }
  ],
  "total_potential_savings": 5420.00,
  "summary": {
    "total_recommendations": 12,
    "by_type": {
      "DOWNSIZE": 5,
      "TERMINATE": 3,
      "RESERVED_INSTANCE": 4
    }
  }
}
```

### Get Cost Forecast

```http
GET /api/costs/forecast?months=3
Authorization: Bearer {token}
```

**Query Parameters:**
- `months` (required): Number of months to forecast (1-12)
- `confidence_level` (optional): 80 | 90 | 95 (default: 95)

**Response: 200 OK**
```json
{
  "forecast": [
    {
      "month": "2024-02",
      "predicted_cost": 11200.00,
      "lower_bound": 10500.00,
      "upper_bound": 12000.00,
      "confidence_level": 95
    }
  ],
  "total_forecasted": 33600.00,
  "trend": "INCREASING",
  "change_percentage": 5.2
}
```

---

## Resource Management Endpoints

Proxied through API Gateway to **resource-scanner** service (Port 8000)

### List AWS Resources

```http
GET /api/resources?service=EC2&region=us-west-2
Authorization: Bearer {token}
```

**Query Parameters:**
- `service` (optional): Filter by service type (`EC2`, `RDS`, `S3`, `Lambda`)
- `region` (optional): Filter by AWS region
- `status` (optional): Filter by status (`RUNNING`, `STOPPED`, `TERMINATED`)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Results per page (default: 50, max: 100)

**Response: 200 OK**
```json
{
  "resources": [
    {
      "resource_id": "i-0123456789abcdef0",
      "resource_type": "EC2",
      "name": "web-server-01",
      "region": "us-west-2",
      "status": "RUNNING",
      "instance_type": "m5.large",
      "launch_time": "2024-01-01T10:00:00Z",
      "monthly_cost": 73.44,
      "tags": {
        "Environment": "production",
        "Team": "backend"
      },
      "metrics": {
        "cpu_utilization": 45.2,
        "memory_utilization": 62.1,
        "network_in": 1024000,
        "network_out": 512000
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 127,
    "total_pages": 3
  }
}
```

### Get Resource Details

```http
GET /api/resources/{resource_id}
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "resource_id": "i-0123456789abcdef0",
  "resource_type": "EC2",
  "name": "web-server-01",
  "region": "us-west-2",
  "availability_zone": "us-west-2a",
  "status": "RUNNING",
  "instance_type": "m5.large",
  "launch_time": "2024-01-01T10:00:00Z",
  "platform": "Linux/UNIX",
  "vpc_id": "vpc-12345678",
  "subnet_id": "subnet-87654321",
  "security_groups": ["sg-11111111"],
  "monthly_cost": 73.44,
  "tags": {
    "Environment": "production",
    "Team": "backend",
    "Owner": "john@example.com"
  },
  "historical_metrics": {
    "cpu_utilization": [
      {"timestamp": "2024-01-15T10:00:00Z", "value": 45.2},
      {"timestamp": "2024-01-15T11:00:00Z", "value": 47.8}
    ]
  }
}
```

**Error Responses:**
- `404 Not Found`: Resource not found

### Scan AWS Account

```http
POST /api/resources/scan
Authorization: Bearer {token}
Content-Type: application/json

{
  "services": ["EC2", "RDS", "S3"],
  "regions": ["us-west-2", "us-east-1"]
}
```

**Response: 202 Accepted**
```json
{
  "scan_id": "scan-550e8400-e29b-41d4",
  "status": "IN_PROGRESS",
  "message": "Resource scan initiated",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

### Get Scan Status

```http
GET /api/resources/scan/{scan_id}
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "scan_id": "scan-550e8400-e29b-41d4",
  "status": "COMPLETED",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:34:23Z",
  "resources_discovered": 127,
  "errors": []
}
```

---

## Analytics & Reporting Endpoints

Proxied through API Gateway to **analytics-engine** service (Port 8003)

### Generate Cost Report

```http
POST /api/reports/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "report_type": "MONTHLY_SUMMARY",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "format": "PDF",
  "include_forecasts": true,
  "include_recommendations": true
}
```

**Report Types:**
- `MONTHLY_SUMMARY`: Monthly cost overview
- `DETAILED_ANALYSIS`: Detailed cost breakdown
- `OPTIMIZATION_REPORT`: Focus on savings opportunities
- `EXECUTIVE_SUMMARY`: High-level summary for executives

**Formats:**
- `PDF`: PDF document
- `EXCEL`: Excel spreadsheet
- `JSON`: JSON data export

**Response: 202 Accepted**
```json
{
  "report_id": "rpt-770e8400-e29b-41d4",
  "status": "GENERATING",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

### Get Report Status

```http
GET /api/reports/{report_id}
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "report_id": "rpt-770e8400-e29b-41d4",
  "status": "COMPLETED",
  "report_type": "MONTHLY_SUMMARY",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z",
  "download_url": "https://costwatch.com/api/reports/rpt-770e8400-e29b-41d4/download",
  "expires_at": "2024-01-22T10:32:15Z"
}
```

### Download Report

```http
GET /api/reports/{report_id}/download
Authorization: Bearer {token}
```

**Response: 200 OK**
- Content-Type: `application/pdf` | `application/vnd.ms-excel` | `application/json`
- Binary file data

### Get Cost Trends

```http
GET /api/analytics/trends?period=90d&metric=total_cost
Authorization: Bearer {token}
```

**Query Parameters:**
- `period`: Time period (`7d`, `30d`, `90d`, `1y`)
- `metric`: Metric to analyze (`total_cost`, `service_count`, `optimization_potential`)
- `group_by` (optional): Group by dimension (`service`, `region`, `account`)

**Response: 200 OK**
```json
{
  "metric": "total_cost",
  "period": "90d",
  "data_points": [
    {
      "date": "2023-10-15",
      "value": 10234.56,
      "change_percentage": 2.3
    }
  ],
  "trend": "INCREASING",
  "average": 10500.00,
  "peak": 12000.00,
  "trough": 9500.00
}
```

---

## Alert Management Endpoints

Proxied through API Gateway to **alert-manager** service (Port 8004)

### List Alerts

```http
GET /api/alerts?status=ACTIVE&severity=HIGH
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (optional): `ACTIVE` | `ACKNOWLEDGED` | `RESOLVED`
- `severity` (optional): `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`
- `alert_type` (optional): `COST_THRESHOLD` | `ANOMALY` | `BUDGET_EXCEEDED`
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 50)

**Response: 200 OK**
```json
{
  "alerts": [
    {
      "alert_id": "alt-880e8400-e29b-41d4",
      "alert_type": "COST_THRESHOLD",
      "severity": "HIGH",
      "status": "ACTIVE",
      "title": "Monthly cost threshold exceeded",
      "description": "AWS monthly spend has exceeded $10,000 threshold",
      "triggered_at": "2024-01-15T10:25:00Z",
      "threshold": 10000.00,
      "current_value": 10543.21,
      "resource_id": null,
      "tags": ["cost", "budget"]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 15
  }
}
```

### Create Alert Rule

```http
POST /api/alerts/rules
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "High Monthly Cost Alert",
  "alert_type": "COST_THRESHOLD",
  "condition": {
    "metric": "monthly_cost",
    "operator": "GREATER_THAN",
    "threshold": 10000.00
  },
  "severity": "HIGH",
  "notification_channels": ["email", "slack"],
  "recipients": ["admin@example.com"],
  "enabled": true
}
```

**Alert Types:**
- `COST_THRESHOLD`: Cost exceeds threshold
- `ANOMALY`: Unusual cost pattern detected
- `BUDGET_EXCEEDED`: Budget limit exceeded
- `RESOURCE_IDLE`: Resource underutilized
- `OPTIMIZATION_AVAILABLE`: New optimization opportunity

**Response: 201 Created**
```json
{
  "rule_id": "rule-990e8400-e29b-41d4",
  "name": "High Monthly Cost Alert",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "ACTIVE"
}
```

### Update Alert Rule

```http
PUT /api/alerts/rules/{rule_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "threshold": 12000.00,
  "enabled": true
}
```

**Response: 200 OK**
```json
{
  "rule_id": "rule-990e8400-e29b-41d4",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Delete Alert Rule

```http
DELETE /api/alerts/rules/{rule_id}
Authorization: Bearer {token}
```

**Response: 204 No Content**

### Acknowledge Alert

```http
POST /api/alerts/{alert_id}/acknowledge
Authorization: Bearer {token}
Content-Type: application/json

{
  "acknowledged_by": "admin@example.com",
  "notes": "Investigating cost spike"
}
```

**Response: 200 OK**
```json
{
  "alert_id": "alt-880e8400-e29b-41d4",
  "status": "ACKNOWLEDGED",
  "acknowledged_at": "2024-01-15T10:40:00Z"
}
```

### Resolve Alert

```http
POST /api/alerts/{alert_id}/resolve
Authorization: Bearer {token}
Content-Type: application/json

{
  "resolved_by": "admin@example.com",
  "resolution_notes": "Optimized EC2 instances, cost back to normal"
}
```

**Response: 200 OK**
```json
{
  "alert_id": "alt-880e8400-e29b-41d4",
  "status": "RESOLVED",
  "resolved_at": "2024-01-15T11:00:00Z"
}
```

---

## Error Responses

All endpoints follow consistent error response format:

### 400 Bad Request

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": [
    {
      "field": "start_date",
      "issue": "Date format must be YYYY-MM-DD"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 401 Unauthorized

```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or expired authentication token",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 403 Forbidden

```json
{
  "error": "FORBIDDEN",
  "message": "Insufficient permissions to access this resource",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 404 Not Found

```json
{
  "error": "NOT_FOUND",
  "message": "Resource not found",
  "resource_type": "alert_rule",
  "resource_id": "rule-990e8400-e29b-41d4",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 429 Too Many Requests

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60,
  "limit": 100,
  "window": "1 minute",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "request_id": "req-abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Rate Limiting

API requests are rate-limited per organization:

| Endpoint Type | Rate Limit |
|--------------|------------|
| Authentication | 10 requests/minute |
| Read operations (GET) | 100 requests/minute |
| Write operations (POST/PUT/DELETE) | 50 requests/minute |
| Resource scans | 5 requests/hour |
| Report generation | 10 requests/hour |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705319400
```

---

## Webhooks

CostWatch can send webhook notifications for events:

### Webhook Events

- `alert.triggered`: New alert created
- `alert.resolved`: Alert resolved
- `cost.threshold_exceeded`: Cost threshold exceeded
- `report.generated`: Report generation completed
- `scan.completed`: Resource scan completed

### Webhook Payload Example

```json
{
  "event": "alert.triggered",
  "event_id": "evt-aa0e8400-e29b-41d4",
  "timestamp": "2024-01-15T10:30:00Z",
  "organization_id": "660e8400-e29b-41d4-a716-446655440000",
  "data": {
    "alert_id": "alt-880e8400-e29b-41d4",
    "alert_type": "COST_THRESHOLD",
    "severity": "HIGH",
    "title": "Monthly cost threshold exceeded",
    "current_value": 10543.21
  }
}
```

### Configuring Webhooks

```http
POST /api/webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/costwatch",
  "events": ["alert.triggered", "alert.resolved"],
  "secret": "your-webhook-secret"
}
```

---

## Pagination

List endpoints support cursor-based pagination:

### Request

```http
GET /api/resources?limit=50&page=2
```

### Response

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 237,
    "total_pages": 5,
    "has_next": true,
    "has_previous": true,
    "next_page": 3,
    "previous_page": 1
  }
}
```

---

## Filtering & Sorting

List endpoints support filtering and sorting:

### Filtering

```http
GET /api/resources?filter[status]=RUNNING&filter[region]=us-west-2
```

### Sorting

```http
GET /api/resources?sort=-monthly_cost,name
```

- Prefix with `-` for descending order
- No prefix for ascending order
- Multiple sort fields separated by comma

---

## API Versioning

The API uses URL versioning. Current version: **v1**

```http
GET /api/v1/costs/monthly
```

When a new version is released, the old version will be supported for at least 12 months.

---

## SDK Examples

### Python

```python
import requests

class CostWatchClient:
    def __init__(self, api_key):
        self.base_url = "https://api.costwatch.com"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_monthly_costs(self, start_date, end_date):
        response = requests.get(
            f"{self.base_url}/api/costs/monthly",
            headers=self.headers,
            params={"start_date": start_date, "end_date": end_date}
        )
        response.raise_for_status()
        return response.json()

client = CostWatchClient("your-api-key")
costs = client.get_monthly_costs("2024-01-01", "2024-12-31")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class CostWatchClient {
  constructor(apiKey) {
    this.baseURL = 'https://api.costwatch.com';
    this.headers = { Authorization: `Bearer ${apiKey}` };
  }

  async getMonthlyCosts(startDate, endDate) {
    const response = await axios.get(`${this.baseURL}/api/costs/monthly`, {
      headers: this.headers,
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  }
}

const client = new CostWatchClient('your-api-key');
const costs = await client.getMonthlyCosts('2024-01-01', '2024-12-31');
```

### cURL

```bash
# Login
curl -X POST https://api.costwatch.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get monthly costs
curl https://api.costwatch.com/api/costs/monthly \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G \
  --data-urlencode "start_date=2024-01-01" \
  --data-urlencode "end_date=2024-12-31"
```

---

## Support

For API support:
- **Documentation**: https://docs.costwatch.com
- **Status Page**: https://status.costwatch.com
- **Support Email**: support@costwatch.com
- **GitHub Issues**: https://github.com/costwatch/costwatch/issues

---

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for API version history and breaking changes.
