# CostWatch Quick Start Guide

Get CostWatch running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- 8GB RAM minimum
- Ports 3000, 5432, 6379, 8000-8004 available

## Quick Start

### Option 1: Using Make (Recommended)

```bash
# Start everything
make start

# Check health
make health

# View logs
make logs

# Stop
make down
```

### Option 2: Using Scripts

```bash
# Start all services
./scripts/start-local.sh

# Test health
./scripts/test-health.sh
```

### Option 3: Manual Docker Compose

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Access the Application

Once services are running:

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8002/docs
- **API Gateway**: http://localhost:8002
- **Resource Scanner**: http://localhost:8000
- **Cost Analyzer**: http://localhost:8001
- **Analytics Engine**: http://localhost:8003
- **Alert Manager**: http://localhost:8004

## Test the API

```bash
# Check all services are healthy
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Scan AWS resources (using mock credentials)
curl -X POST http://localhost:8000/scan/all \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-west-2"], "include_costs": true}'

# Analyze costs
curl -X POST http://localhost:8001/analyze/costs \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "000000000000",
    "start_date": "2025-01-01",
    "end_date": "2025-01-15"
  }'

# Get analytics dashboard
curl "http://localhost:8003/analytics/dashboard/000000000000?period=last_30_days"
```

## Environment Variables

Copy and customize environment files:

```bash
# Backend services use docker-compose.yml defaults
# Or create .env file
cp .env.example .env

# Frontend
cd frontend
cp .env.example .env.local
```

## Troubleshooting

### Services won't start

```bash
# Clean everything and restart
make clean
make build
make up
```

### Port conflicts

Check if ports are in use:

```bash
lsof -i :3000  # Frontend
lsof -i :8002  # API Gateway
```

### View service logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f cost-analyzer
```

### Database issues

```bash
# Restart database
docker-compose restart postgres

# Access database
docker-compose exec postgres psql -U costwatch_user -d costwatch
```

## Next Steps

1. **Configure AWS Credentials**: Update `.env` with your AWS credentials
2. **Explore API Docs**: Visit http://localhost:8002/docs
3. **Check Examples**: See `docs/API_EXAMPLES.md` for detailed API usage
4. **Deploy**: See `docs/DEPLOYMENT.md` for production deployment

## Common Commands

```bash
# Restart a service
docker-compose restart <service-name>

# Rebuild a service
docker-compose build <service-name>
docker-compose up -d <service-name>

# View resource usage
docker stats

# Clean up
docker-compose down -v  # Remove volumes too
```

## Need Help?

- **Documentation**: Check `/docs` folder
- **API Reference**: `docs/API_REFERENCE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Issues**: https://github.com/ArsalanAnwer0/CostWatch/issues

## Development

For development with hot reload:

```bash
# Use the simple compose file
docker-compose -f docker-compose.simple.yml up
```

Happy cost optimizing! 💰
