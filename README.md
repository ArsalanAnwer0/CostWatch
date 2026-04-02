# CostWatch

Track and visualize AWS resource costs across your organization.

## What this project is

CostWatch is a learning project built to develop real-world skills in:

- **Backend APIs** — FastAPI microservices with JWT auth and inter-service communication
- **Docker & Kubernetes** — containerized services with K8s deployments, services, ConfigMaps, Secrets, and RBAC
- **AWS & Cloud Infra** — Terraform for VPC, EKS, and RDS; boto3 for AWS resource scanning and Cost Explorer integration
- **Observability** — Prometheus metrics and Grafana dashboards

## What it does

1. **Scans** your AWS account for active resources (EC2, RDS, S3, etc.)
2. **Tracks** daily cost data via the AWS Cost Explorer API
3. **Visualizes** cost trends over time on a minimal React dashboard

## Architecture

```
frontend (React)
    └── api-gateway (FastAPI, port 8002)   ← auth + routing
            ├── cost-service (FastAPI, port 8001)   ← cost data & trends
            └── resource-scanner (Flask, port 8000) ← AWS resource discovery

PostgreSQL (database)
Prometheus + Grafana (monitoring)
```

## Running locally

**Prerequisites:** Docker, Docker Compose

```bash
cp .env.example .env
# Add your AWS credentials to .env (optional — services return mock data without them)

docker-compose up -d
```

- Frontend: http://localhost:3000
- API Gateway docs: http://localhost:8002/docs
- Cost Service docs: http://localhost:8001/docs
- Resource Scanner docs: http://localhost:8000/docs

## Deploying to AWS

**Prerequisites:** Terraform, kubectl, AWS CLI

```bash
# Provision infra (VPC, EKS, RDS)
cd infrastructure/terraform/environments/dev
terraform init && terraform apply

# Deploy to Kubernetes
kubectl apply -k k8s/
```

## Project structure

```
CostWatch/
├── services/
│   ├── api-gateway/           # FastAPI — auth, routing
│   ├── cost-service/          # FastAPI — AWS cost data
│   └── resource-scanner/      # Flask — AWS resource discovery
├── frontend/                  # React — minimal dashboard
├── database/schemas/          # PostgreSQL schema (2 files)
├── k8s/                       # Kubernetes manifests
├── infrastructure/terraform/  # AWS infra (VPC, EKS, RDS)
├── monitoring/                # Prometheus + Grafana
├── docker-compose.yml
└── .env.example
```

## Environment variables

See `.env.example` for all required variables. AWS credentials are optional for local development — services fall back to mock data.
