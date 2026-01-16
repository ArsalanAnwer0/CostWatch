# CostWatch Local Setup Guide

This guide will help you get CostWatch running on your local machine for development and testing purposes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

### Verify Prerequisites

```bash
docker --version
docker-compose --version
git --version
```

## Quick Start

Follow these steps to get CostWatch running on localhost:

### 1. Clone the Repository

```bash
git clone https://github.com/ArsalanAnwer0/CostWatch.git
cd CostWatch
```

### 2. Environment Configuration

The repository includes a `.env` file with local development settings. You can use it as-is for local testing, or customize it if needed.

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (change in production)
- `AWS_*`: Mock AWS credentials for local development

### 3. Start All Services

Build and start all containers in detached mode:

```bash
docker-compose up -d
```

This command will:
- Build Docker images for all 5 microservices
- Start PostgreSQL database and initialize schema
- Start Redis cache
- Start all microservices (api-gateway, resource-scanner, cost-analyzer, analytics-engine, alert-manager)
- Start Nginx reverse proxy

### 4. Monitor Startup Progress

Watch the logs to ensure all services start successfully:

```bash
docker-compose logs -f
```

Press `Ctrl+C` to stop following logs. Services are ready when you see health check successes.

### 5. Verify Services Are Running

Check that all containers are healthy:

```bash
docker-compose ps
```

All services should show status as "Up" or "Up (healthy)".

## Access the Application

Once all services are running, you can access CostWatch:

### Web Interfaces

- **API Documentation (Swagger UI)**: http://localhost/docs
- **Alternative API Docs (ReDoc)**: http://localhost/redoc
- **Nginx Health Check**: http://localhost/health

### Direct Service Access

If you need to access services directly (bypassing Nginx):

- **API Gateway**: http://localhost:8002
- **Resource Scanner**: http://localhost:8000
- **Cost Analyzer**: http://localhost:8001
- **Analytics Engine**: http://localhost:8003
- **Alert Manager**: http://localhost:8004

### Database Access

Connect to PostgreSQL:

```bash
docker-compose exec postgres psql -U costwatch_user -d costwatch
```

Or using external tools:
- Host: localhost
- Port: 5432
- Database: costwatch
- Username: costwatch_user
- Password: costwatch_password

### Redis Access

Connect to Redis CLI:

```bash
docker-compose exec redis redis-cli
```

## Testing the API

### Health Checks

Test individual service health endpoints:

```bash
# API Gateway
curl http://localhost:8002/health

# Resource Scanner
curl http://localhost:8000/health

# Cost Analyzer
curl http://localhost:8001/health

# Analytics Engine
curl http://localhost:8003/health

# Alert Manager
curl http://localhost:8004/health
```

### Authentication

Register a new user:

```bash
curl -X POST http://localhost:8002/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

Login to get JWT token:

```bash
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### Cost Analysis

Get monthly cost summary (requires authentication):

```bash
curl http://localhost:8002/costs/monthly \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Common Commands

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove All Data

```bash
docker-compose down -v
```

Warning: This will delete all database data and Redis cache.

### Restart a Specific Service

```bash
docker-compose restart api-gateway
```

### View Logs for a Specific Service

```bash
docker-compose logs -f api-gateway
```

### Rebuild a Service

If you make code changes:

```bash
docker-compose build api-gateway
docker-compose up -d api-gateway
```

### Rebuild All Services

```bash
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Issue: Port Already in Use

**Symptom**: Error message about port 80, 5432, 6379, or 8000-8004 already in use.

**Solution**: Stop the conflicting service or change ports in `docker-compose.yml`.

Find which process is using a port:
```bash
# macOS/Linux
lsof -i :80

# Or kill all Docker containers
docker-compose down
```

### Issue: Services Not Starting

**Symptom**: Container exits immediately or shows unhealthy status.

**Solution**: Check logs for specific error messages:

```bash
docker-compose logs <service-name>
```

Common causes:
- Missing environment variables
- Database not ready (wait for postgres health check)
- Port conflicts

### Issue: Database Connection Failed

**Symptom**: Services can't connect to PostgreSQL.

**Solution**:

1. Verify postgres container is running and healthy:
```bash
docker-compose ps postgres
```

2. Check database logs:
```bash
docker-compose logs postgres
```

3. Restart database:
```bash
docker-compose restart postgres
```

### Issue: Nginx 502 Bad Gateway

**Symptom**: Nginx returns 502 error when accessing http://localhost.

**Solution**:

1. Verify all backend services are healthy:
```bash
docker-compose ps
```

2. Check service logs:
```bash
docker-compose logs api-gateway
```

3. Verify services are accessible directly:
```bash
curl http://localhost:8002/health
```

### Issue: Permission Denied Errors

**Symptom**: Permission errors when building or running containers.

**Solution**:

1. Ensure Docker daemon is running
2. Add your user to docker group (Linux):
```bash
sudo usermod -aG docker $USER
```
3. Restart Docker Desktop (macOS/Windows)

### Issue: Out of Disk Space

**Symptom**: Build failures or "no space left on device" errors.

**Solution**:

Clean up Docker resources:
```bash
docker system prune -a --volumes
```

Warning: This removes all unused containers, networks, images, and volumes.

## Development Workflow

### Making Code Changes

1. Edit code in `services/<service-name>/app/`
2. Rebuild the service:
```bash
docker-compose build <service-name>
docker-compose up -d <service-name>
```
3. Test your changes
4. View logs:
```bash
docker-compose logs -f <service-name>
```

### Running Tests

Execute tests inside a service container:

```bash
docker-compose exec api-gateway pytest tests/
```

### Database Migrations

Access postgres and run migrations:

```bash
docker-compose exec postgres psql -U costwatch_user -d costwatch -f /path/to/migration.sql
```

## Architecture Overview

CostWatch runs with the following components:

1. **PostgreSQL** (port 5432): Main database storing users, AWS resources, costs, alerts
2. **Redis** (port 6379): Caching layer for improved performance
3. **API Gateway** (port 8002): Main entry point, handles authentication and routing
4. **Resource Scanner** (port 8000): Scans AWS resources (EC2, RDS, S3)
5. **Cost Analyzer** (port 8001): Analyzes costs and provides optimization recommendations
6. **Analytics Engine** (port 8003): Machine learning predictions and reporting
7. **Alert Manager** (port 8004): Manages cost alerts and notifications
8. **Nginx** (port 80/443): Reverse proxy with rate limiting and load balancing

All services communicate through the `costwatch-network` Docker network.

## Next Steps

After getting the application running locally:

1. Explore the API documentation at http://localhost/docs
2. Register a test user account
3. Add AWS account credentials (mock or real)
4. Trigger a resource scan
5. View cost analysis and recommendations
6. Set up cost alerts

## Support

For issues, questions, or contributions:

- GitHub Issues: https://github.com/ArsalanAnwer0/CostWatch/issues
- Documentation: See other files in `docs/` directory
- API Reference: See `docs/API_REFERENCE.md`

## Security Note

The `.env` file contains development credentials. Never use these credentials in production. Always:

- Change all passwords and secret keys
- Use real AWS IAM roles instead of access keys
- Enable HTTPS with valid SSL certificates
- Configure proper CORS origins
- Implement rate limiting and authentication for production use
