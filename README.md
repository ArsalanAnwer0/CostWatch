# CostWatch 💰

Smart cloud cost optimization platform that helps companies reduce AWS spending by 35% through intelligent monitoring and automated recommendations.

**✨ Now 100% Functional** - Complete with working frontend dashboard, mock data, and full backend API integration!

## Project Overview

CostWatch solves the cloud waste crisis by providing real-time AWS cost monitoring, automated waste detection, and intelligent optimization recommendations. Built with enterprise-grade microservices architecture and modern DevOps practices.

## Business Impact

- Average cost reduction through intelligent resource optimization
- Cost alerts preventing surprise AWS bills
- Automated waste detection for unused EC2, storage, and services
- Predictive analytics for budget forecasting and capacity planning

## Problem Solved

Companies waste millions on cloud infrastructure because they lack visibility into spending patterns. CostWatch provides the intelligence and automation needed to optimize cloud costs continuously.

## Technology Stack

### Backend Services
- API Gateway: FastAPI with async support and auto-generated OpenAPI docs
- Microservices: Flask and FastAPI optimized for different service needs
- Database: PostgreSQL (AWS RDS) with Redis caching layer
- Message Queue: AWS SQS for asynchronous processing

### Infrastructure and DevOps
- Containerization: Docker with multi-stage builds for optimization
- Orchestration: Kubernetes (AWS EKS) with auto-scaling policies
- Infrastructure as Code: Terraform with modular, reusable components
- Configuration Management: Ansible for automated system configuration
- CI/CD: GitHub Actions with multi-environment deployment pipeline

### Monitoring and Observability
- Metrics Collection: Prometheus with custom business and technical metrics
- Visualization: Grafana dashboards for operational and executive views
- Log Aggregation: ELK Stack for centralized logging and analysis
- Alerting: Multi-channel notifications with smart escalation policies

## Key Features

### Cost Optimization
- Real-time cost tracking across all AWS services
- Waste detection for idle EC2 instances and unattached EBS volumes
- Right-sizing recommendations based on actual usage patterns
- Budget forecasting with machine learning predictions

### Intelligence and Analytics
- Historical cost trend analysis and anomaly detection
- Resource utilization insights for CPU, memory, and storage
- Custom dashboards for executive and operational teams
- ROI tracking for optimization recommendations

### Proactive Alerting
- Budget alerts with intelligent threshold management
- Machine learning-powered spending anomaly detection
- Multi-channel notifications via Slack, email, and webhooks
- Escalation policies for appropriate team routing

### Reporting and Compliance
- Executive dashboards with key cost metrics
- Department and project-based cost allocation
- Governance and policy adherence monitoring
- Automated scheduled reporting

## Project Structure

```
costwatch/
├── .github/workflows/          # CI/CD pipelines and automation
├── infrastructure/
│   ├── terraform/             # Infrastructure as Code
│   └── ansible/               # Configuration management
├── services/                  # Microservices applications
│   ├── api-gateway/          # FastAPI gateway service
│   ├── resource-scanner/     # AWS resource discovery service
│   ├── cost-analyzer/        # Cost optimization engine
│   ├── alert-manager/        # Notification and alerting system
│   └── analytics-engine/     # Machine learning and analytics
├── k8s/                      # Kubernetes manifests
├── monitoring/               # Observability configurations
├── scripts/                  # Automation and utility scripts
├── docs/                     # Project documentation
└── tests/                    # Test suites
```

## Getting Started

### ⚡ Instant Demo (No Backend Required!)

The frontend works immediately with mock AWS data:

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000`, login with any email/password, and explore the fully functional dashboard!

### 🚀 Full Stack Setup

Get the complete CostWatch platform running:

#### Prerequisites
- Docker 20.10 or higher
- docker-compose 2.0 or higher
- Node.js 18+ (for frontend development)

#### Option 1: Automated Startup (Recommended)

```bash
# Clone the repository
git clone https://github.com/ArsalanAnwer0/CostWatch.git
cd CostWatch

# Run the startup script
./scripts/start-local.sh
```

The script will:
- Check prerequisites
- Build all Docker containers
- Start all services
- Display access URLs

#### Option 2: Manual Startup

```bash
# Clone the repository
git clone https://github.com/ArsalanAnwer0/CostWatch.git
cd CostWatch

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Access the Application

Once running, access CostWatch at:

- **API Documentation**: http://localhost/docs
- **API Alternative Docs**: http://localhost/redoc
- **Health Check**: http://localhost/health

Direct service endpoints:
- API Gateway: http://localhost:8002
- Resource Scanner: http://localhost:8000
- Cost Analyzer: http://localhost:8001
- Analytics Engine: http://localhost:8003
- Alert Manager: http://localhost:8004

#### Default Credentials

Database:
- Host: localhost:5432
- Database: costwatch
- Username: costwatch_user
- Password: costwatch_password

Redis:
- Host: localhost:6379

#### Testing the API

Register a new user:
```bash
curl -X POST http://localhost:8002/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!", "full_name": "Test User"}'
```

Login:
```bash
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

#### Common Commands

```bash
# Stop all services
docker-compose down

# View service status
docker-compose ps

# View logs for specific service
docker-compose logs -f api-gateway

# Restart a service
docker-compose restart api-gateway

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

#### Troubleshooting

For detailed setup instructions and troubleshooting, see [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

Common issues:
- Port conflicts: Stop services using ports 80, 5432, 6379, 8000-8004
- Docker not running: Start Docker Desktop or Docker daemon
- Build failures: Ensure sufficient disk space with `docker system prune`

### Production Deployment

#### Prerequisites
- AWS CLI configured with appropriate IAM permissions
- Terraform 1.0 or higher
- kubectl 1.24 or higher
- Docker 20.10 or higher
- Python 3.9 or higher

#### Quick Start
```bash
# Clone the repository
git clone https://github.com/ArsalanAnwer0/CostWatch.git
cd costwatch

# Set up local development environment
make setup

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Deploy services to Kubernetes
cd ../../scripts
./deploy.sh

# Access the platform
kubectl get ingress costwatch-gateway
```

### Local Development
```bash
# Start local development environment
docker-compose up -d

# Run tests
make test

# View logs
make logs

# Clean up
make clean
```

- Vulnerability Scanning: Automated security assessments

## Documentation

- Architecture Overview - System design and components
- API Documentation - RESTful API reference
- Deployment Guide - Step-by-step deployment instructions
- Monitoring Setup - Observability configuration

## License

This project is licensed under the MIT License. See the LICENSE file for details.
