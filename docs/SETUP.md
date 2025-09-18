# CostWatch Setup Guide

## System Requirements

### Development Environment
- **Operating System**: macOS 10.15+, Ubuntu 20.04+, or Windows 10+ with WSL2
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 20GB available disk space
- **Docker**: Docker Desktop 4.0+ with Docker Compose
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.11 or higher

### Production Environment
- **Kubernetes**: Version 1.24 or higher
- **Database**: PostgreSQL 15+ with 100GB+ storage
- **Cache**: Redis 7.0+ with 4GB+ memory
- **Load Balancer**: AWS ALB or equivalent
- **SSL Certificate**: Valid TLS certificate for HTTPS

## Local Development Setup

### Step 1: Environment Preparation
```bash
# Clone the repository
git clone https://github.com/your-username/costwatch.git
cd costwatch

# Verify system requirements
python --version  # Should be 3.11+
node --version    # Should be 18.0+
docker --version  # Should be 20.10+
```

### Step 2: Database Initialization
```bash
# Start PostgreSQL with Docker (if not installed locally)
docker run -d --name postgres-costwatch \
  -e POSTGRES_DB=costwatch_db \
  -e POSTGRES_USER=costwatch_user \
  -e POSTGRES_PASSWORD=costwatch_pass123 \
  -p 5432:5432 postgres:15

# Initialize database schema
./database/init_db.sh

# Verify database setup
./database/init_db.sh --verify
```

### Step 3: Service Configuration
```bash
# Copy environment templates
cp config/templates/.env.template services/api-gateway/.env
cp config/templates/.env.template services/cost-analyzer/.env
cp config/templates/.env.template services/resource-scanner/.env
cp config/templates/.env.template services/analytics-engine/.env
cp config/templates/.env.template services/alert-manager/.env

# Update database connection in each .env file
# Edit each file and update:
# DATABASE_URL=postgresql://costwatch_user:costwatch_pass123@localhost:5432/costwatch_db
```

### Step 4: Backend Services
```bash
# Build and start all services
docker-compose up --build -d

# Verify services are running
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Cost Analyzer
curl http://localhost:8002/health  # Resource Scanner
curl http://localhost:8003/health  # Analytics Engine
curl http://localhost:8004/health  # Alert Manager

# View service logs
docker-compose logs -f api-gateway
```

### Step 5: Frontend Dashboard
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Access dashboard at http://localhost:3000
```

## Production Setup

### AWS Infrastructure Deployment
```bash
# Configure AWS credentials
aws configure

# Navigate to Terraform configuration
cd infrastructure/terraform/environments/prod

# Initialize Terraform
terraform init -backend-config=backend.hcl

# Review deployment plan
terraform plan -var-file=terraform.tfvars

# Deploy infrastructure
terraform apply -var-file=terraform.tfvars
```

### Kubernetes Application Deployment
```bash
# Update kubeconfig for EKS cluster
aws eks update-kubeconfig --region us-west-2 --name costwatch-prod-cluster

# Deploy application using production script
./scripts/deploy-production.sh

# Verify deployment
kubectl get pods -n costwatch
kubectl get services -n costwatch
```

## Configuration Management

### Environment Variables
Each service requires specific environment variables:

**Required Variables**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: JWT signing secret
- `AWS_REGION`: Primary AWS region
- `ENVIRONMENT`: Deployment environment (dev/staging/prod)

**AWS Integration**
- `AWS_ACCESS_KEY_ID`: AWS access key (or use IAM roles)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (or use IAM roles)
- `AWS_ACCOUNT_ID`: Target AWS account for cost analysis

### Database Configuration
```sql
-- Verify database setup
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check sample data
SELECT COUNT(*) FROM organizations;
SELECT COUNT(*) FROM users;
```

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Verify connection parameters
psql -h localhost -U costwatch_user -d costwatch_db

# Reset database if needed
./database/init_db.sh --clean
```

#### Service Health Check Failed
```bash
# Check service logs
docker-compose logs service-name

# Verify environment variables
docker-compose exec api-gateway env | grep DATABASE

# Restart specific service
docker-compose restart api-gateway
```

#### Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

## Performance Optimization

### Database Tuning
```sql
-- Monitor query performance
EXPLAIN ANALYZE SELECT * FROM cost_data WHERE cost_date >= '2024-01-01';

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats WHERE tablename = 'cost_data';
```

### Service Scaling
```bash
# Scale services in Docker Compose
docker-compose up --scale cost-analyzer=3

# Monitor resource usage
docker stats
```

## Security Configuration

### SSL/TLS Setup
```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure nginx for HTTPS
# Update nginx/nginx.conf with SSL settings
```

### AWS IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetDimensionValues",
        "ce:GetReservationCoverage",
        "ce:GetReservationPurchaseRecommendation",
        "ce:GetReservationUtilization",
        "ce:ListCostCategoryDefinitions"
      ],
      "Resource": "*"
    }
  ]
}
```

## Monitoring Setup

### Prometheus Configuration
```bash
# Verify Prometheus is scraping targets
curl http://localhost:9090/api/v1/targets

# Check service metrics
curl http://localhost:8000/metrics
```

### Grafana Dashboard Import
```bash
# Access Grafana at http://localhost:3000
# Username: admin, Password: admin123
# Import dashboard from monitoring/grafana/dashboards/
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
pg_dump -h localhost -U costwatch_user costwatch_db > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U costwatch_user -d costwatch_db < backup_20240101.sql
```

### Configuration Backup
```bash
# Backup environment configurations
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ services/*/.*env
```

---

This setup guide provides comprehensive instructions for both development and production environments. Follow the steps sequentially for successful deployment.