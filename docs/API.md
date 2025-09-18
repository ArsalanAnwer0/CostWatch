# CostWatch API Reference

## Overview

The CostWatch API provides comprehensive programmatic access to all cost management and optimization features. All APIs follow RESTful principles with JSON request/response formats and standardized HTTP status codes.

**Base URL**: `http://localhost:8000/api/v1` (development)  
**Production URL**: `https://api.costwatch.com/api/v1`

## Authentication

### JWT Token Authentication

All API requests require a valid JWT token in the Authorization header:
```http
Authorization: Bearer <jwt_token>
```

### Obtaining Access Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user"
  }
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": "Field 'start_date' is required",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Cost Analysis API

### Get Cost Summary
Retrieve aggregate cost data for specified time period.

```http
GET /api/v1/costs/summary?period=30d&granularity=daily
```

**Query Parameters:**
- `period` (string): Time period - 7d, 30d, 90d, 365d
- `granularity` (string): Data granularity - hourly, daily, weekly, monthly
- `service` (string, optional): Filter by AWS service
- `region` (string, optional): Filter by AWS region

**Response:**
```json
{
  "data": {
    "total_cost": 2847.52,
    "period": "30d",
    "currency": "USD",
    "breakdown": [
      {
        "date": "2024-01-15",
        "cost": 94.58,
        "services": {
          "EC2": 45.30,
          "RDS": 28.15,
          "S3": 21.13
        }
      }
    ],
    "trends": {
      "percentage_change": 12.5,
      "trend_direction": "increasing"
    }
  }
}
```

### Get Cost Trends
Analyze cost trends and patterns over time.

```http
GET /api/v1/costs/trends?start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `group_by` (string): Group by service, region, or account
- `include_forecast` (boolean): Include forecast data

**Response:**
```json
{
  "data": {
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "trends": [
      {
        "date": "2024-01-01",
        "actual_cost": 89.45,
        "forecasted_cost": 92.30
      }
    ],
    "insights": {
      "average_daily_cost": 91.85,
      "peak_cost_date": "2024-01-15",
      "cost_variance": 8.2
    }
  }
}
```

### Get Cost Forecasts
Retrieve ML-generated cost predictions.

```http
GET /api/v1/costs/forecasts?horizon=30&confidence_level=0.95
```

**Query Parameters:**
- `horizon` (integer): Forecast horizon in days
- `confidence_level` (float): Confidence level (0.8, 0.9, 0.95)
- `model_version` (string, optional): Specific model version

**Response:**
```json
{
  "data": {
    "forecasts": [
      {
        "date": "2024-02-01",
        "predicted_cost": 95.30,
        "confidence_interval": {
          "lower": 88.45,
          "upper": 102.15
        },
        "confidence_score": 0.92
      }
    ],
    "model_info": {
      "version": "v2.1.0",
      "accuracy": 0.94,
      "last_trained": "2024-01-10T08:00:00Z"
    }
  }
}
```

## Resource Management API

### List AWS Resources
Retrieve discovered AWS resources with metadata.

```http
GET /api/v1/resources?service=ec2&region=us-west-2&limit=50&offset=0
```

**Query Parameters:**
- `service` (string, optional): AWS service type
- `region` (string, optional): AWS region
- `state` (string, optional): Resource state
- `limit` (integer): Number of results (max 100)
- `offset` (integer): Pagination offset

**Response:**
```json
{
  "data": {
    "resources": [
      {
        "id": "uuid",
        "resource_id": "i-1234567890abcdef0",
        "resource_name": "web-server-01",
        "service_type": "ec2",
        "resource_type": "t3.medium",
        "region": "us-west-2",
        "state": "running",
        "monthly_cost": 124.50,
        "tags": {
          "Environment": "production",
          "Team": "web"
        },
        "last_seen": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 142,
      "limit": 50,
      "offset": 0,
      "has_more": true
    }
  }
}
```

### Get Resource Details
Retrieve detailed information for specific resource.

```http
GET /api/v1/resources/{resource_id}
```

**Response:**
```json
{
  "data": {
    "resource": {
      "id": "uuid",
      "resource_id": "i-1234567890abcdef0",
      "service_type": "ec2",
      "details": {
        "instance_type": "t3.medium",
        "platform": "Linux/UNIX",
        "vpc_id": "vpc-12345678",
        "subnet_id": "subnet-12345678",
        "security_groups": ["sg-12345678"]
      },
      "cost_history": [
        {
          "date": "2024-01-15",
          "cost": 4.15
        }
      ],
      "utilization": {
        "cpu_average": 25.5,
        "memory_average": 45.2,
        "network_in": 1024000,
        "network_out": 512000
      }
    }
  }
}
```

### Trigger Resource Scan
Initiate scan for AWS resources.

```http
POST /api/v1/resources/scan
Content-Type: application/json

{
  "services": ["ec2", "rds", "s3"],
  "regions": ["us-west-2", "us-east-1"],
  "scan_type": "full"
}
```

**Response:**
```json
{
  "data": {
    "scan_job_id": "uuid",
    "status": "started",
    "estimated_duration": "5-10 minutes",
    "services": ["ec2", "rds", "s3"],
    "regions": ["us-west-2", "us-east-1"]
  }
}
```

## Analytics & Optimization API

### Get Optimization Recommendations
Retrieve AI-generated cost optimization suggestions.

```http
GET /api/v1/analytics/recommendations?category=rightsizing&status=pending
```

**Query Parameters:**
- `category` (string): rightsizing, reserved_instances, spot_instances, storage
- `status` (string): pending, accepted, rejected, implemented
- `min_savings` (float): Minimum savings threshold

**Response:**
```json
{
  "data": {
    "recommendations": [
      {
        "id": "uuid",
        "type": "rightsizing",
        "title": "Downsize EC2 Instance",
        "description": "Instance shows low CPU utilization. Downsize from t3.medium to t3.small.",
        "resource_id": "i-1234567890abcdef0",
        "potential_savings": 120.00,
        "confidence_score": 0.85,
        "effort_level": "low",
        "implementation": {
          "steps": [
            "Create AMI snapshot",
            "Launch new t3.small instance",
            "Update load balancer targets"
          ],
          "estimated_downtime": "5 minutes"
        },
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### Generate Cost Report
Create detailed cost analysis report.

```http
POST /api/v1/analytics/reports
Content-Type: application/json

{
  "report_type": "monthly_summary",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "format": "pdf",
  "include_recommendations": true,
  "email_recipients": ["manager@company.com"]
}
```

**Response:**
```json
{
  "data": {
    "report_id": "uuid",
    "status": "generating",
    "estimated_completion": "2024-01-15T10:35:00Z",
    "download_url": null
  }
}
```

## Alert Management API

### List Active Alerts
Retrieve current active alerts.

```http
GET /api/v1/alerts?severity=high&status=active
```

**Response:**
```json
{
  "data": {
    "alerts": [
      {
        "id": "uuid",
        "title": "Monthly Budget Exceeded",
        "description": "Current month spending has exceeded budget by 15%",
        "severity": "high",
        "status": "active",
        "triggered_at": "2024-01-15T10:30:00Z",
        "resource_id": null,
        "alert_rule_id": "uuid",
        "trigger_data": {
          "current_spend": 1150.00,
          "budget_limit": 1000.00,
          "threshold_percentage": 100
        }
      }
    ]
  }
}
```

### Create Alert Rule
Create new cost monitoring alert rule.

```http
POST /api/v1/alerts/rules
Content-Type: application/json

{
  "name": "High Daily Cost Alert",
  "description": "Alert when daily costs exceed $100",
  "alert_type": "cost_threshold",
  "conditions": {
    "metric": "daily_cost",
    "operator": "greater_than",
    "threshold": 100.00,
    "period": "daily"
  },
  "severity": "medium",
  "notification_channels": ["email", "slack"],
  "notification_settings": {
    "email_recipients": ["admin@company.com"],
    "slack_channel": "#cost-alerts"
  }
}
```

### Acknowledge Alert
Acknowledge an active alert.

```http
PUT /api/v1/alerts/{alert_id}/acknowledge
Content-Type: application/json

{
  "notes": "Investigating the cost spike in EC2 instances"
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Cost analysis endpoints**: 100 requests per hour
- **Resource scanning**: 10 scans per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Webhooks

Register webhooks to receive real-time notifications:

```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/costwatch",
  "events": ["alert.triggered", "scan.completed"],
  "secret": "your_webhook_secret"
}
```

## SDK and Client Libraries

Official client libraries are available for:

- **Python**: `pip install costwatch-sdk`
- **JavaScript**: `npm install @costwatch/sdk`
- **Go**: `go get github.com/costwatch/go-sdk`

Example Python usage:
```python
from costwatch import CostWatchClient

client = CostWatchClient(
    api_key="your_api_key",
    base_url="https://api.costwatch.com"
)

# Get cost summary
summary = client.costs.get_summary(period="30d")
print(f"Total cost: ${summary.total_cost}")
```

---

This API reference provides comprehensive documentation for integrating with the CostWatch platform programmatically.