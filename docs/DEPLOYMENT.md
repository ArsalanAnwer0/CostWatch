# CostWatch Deployment Guide

## Deployment Overview

CostWatch supports multiple deployment strategies to accommodate different organizational needs, from development environments to enterprise-scale production deployments.

## Deployment Options

### 1. Local Development
- Docker Compose for quick setup
- Suitable for development and testing
- Minimal resource requirements

### 2. Cloud Native (Recommended)
- Kubernetes on AWS EKS
- Auto-scaling and high availability
- Production-ready with monitoring

### 3. Traditional VM Deployment
- Docker containers on EC2 instances
- Suitable for legacy infrastructure
- Manual scaling required

## Prerequisites

### AWS Account Setup

1. **Create AWS Account**
   - Ensure billing is enabled
   - Set up Cost Explorer access
   - Configure trusted advisor

2. **IAM Configuration**
```bash
# Create IAM user for CostWatch
aws iam create-user --user-name costwatch-service

# Attach required policies
aws iam attach-user-policy --user-name costwatch-service \
  --policy-arn arn:aws:iam::aws:policy/CEFullAccess

# Create access keys
aws iam create-access-key --user-name costwatch-service
```

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetDimensionValues",
        "ce:GetUsageReport",
        "ce:DescribeCostCategoryDefinition",
        "organizations:ListAccounts",
        "organizations:DescribeOrganization",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "rds:DescribeDBInstances",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    }
  ]
}
```

## Production Deployment (AWS EKS)

### Step 1: Infrastructure Provisioning

#### Configure Terraform Backend

```bash
cd infrastructure/terraform/environments/prod

# Update backend.hcl with your S3 bucket
cat > backend.hcl << EOF
bucket = "your-terraform-state-bucket"
key    = "costwatch/prod/terraform.tfstate"
region = "us-west-2"
EOF
```

#### Update Variables

```bash
# Edit terraform.tfvars
nano terraform.tfvars

# Update these values:
aws_region = "us-west-2"
environment = "prod"
project_name = "costwatch"

# VPC Configuration
vpc_cidr = "10.1.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

# EKS Configuration
cluster_version = "1.28"
node_instance_types = ["t3.large"]
min_nodes = 2
max_nodes = 10
desired_nodes = 3

# Database Configuration
db_instance_class = "db.t3.small"
db_allocated_storage = 100
db_backup_retention_period = 30
```

#### Deploy Infrastructure

```bash
# Initialize Terraform
terraform init -backend-config=backend.hcl

# Plan deployment
terraform plan -var-file=terraform.tfvars

# Apply infrastructure changes
terraform apply -var-file=terraform.tfvars

# Note the outputs for later use
terraform output
```

### Step 2: Kubernetes Configuration

#### Update Kubeconfig

```bash
# Configure kubectl for EKS cluster
aws eks update-kubeconfig --region us-west-2 --name costwatch-prod-cluster

# Verify cluster access
kubectl get nodes
```

#### Configure Secrets

```bash
# Create namespace
kubectl create namespace costwatch

# Create database secret
kubectl create secret generic costwatch-secrets \
  --from-literal=DATABASE_PASSWORD='your-db-password' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret' \
  --from-literal=AWS_ACCESS_KEY_ID='your-aws-key' \
  --from-literal=AWS_SECRET_ACCESS_KEY='your-aws-secret' \
  -n costwatch
```

#### Update ConfigMaps

```bash
# Update database host in ConfigMap
kubectl edit configmap costwatch-config -n costwatch

# Update DATABASE_HOST to RDS endpoint from Terraform output
```

### Step 3: Application Deployment

#### Build and Push Images

```bash
# Get ECR login token
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and push each service
services=("api-gateway" "cost-analyzer" "resource-scanner" "analytics-engine" "alert-manager")

for service in "${services[@]}"; do
  echo "Building $service..."
  docker build -t costwatch-$service services/$service/
  docker tag costwatch-$service:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/costwatch-$service:latest
  docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/costwatch-$service:latest
done
```

#### Deploy Application

```bash
# Deploy using automated script
./scripts/deploy-production.sh

# Or deploy manually
kubectl apply -k k8s/

# Verify deployment
kubectl get pods -n costwatch
kubectl get services -n costwatch
```

#### Configure Ingress

```bash
# Install AWS Load Balancer Controller
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yaml

# Deploy ingress
kubectl apply -f k8s/ingress/costwatch-ingress.yaml

# Get load balancer URL
kubectl get ingress -n costwatch
```

## Staging Deployment

### Quick Staging Setup
```bash
# Deploy staging environment
cd infrastructure/terraform/environments/staging
terraform init -backend-config=backend.hcl
terraform apply -var-file=terraform.tfvars

# Update kubeconfig for staging
aws eks update-kubeconfig --region us-west-2 --name costwatch-staging-cluster

# Deploy staging application
kubectl create namespace costwatch
kubectl apply -k k8s/
```

## Development Environment

### Docker Compose Deployment
```bash
# Clone repository
git clone https://github.com/your-username/costwatch.git
cd costwatch

# Start services
docker-compose up -d

# Initialize database
./database/init_db.sh

# Verify services
curl http://localhost:8000/health
```

### Local Kubernetes (minikube)
```bash
# Start minikube
minikube start --memory=8192 --cpus=4

# Deploy to local cluster
kubectl apply -k k8s/

# Access services
minikube service api-gateway-service -n costwatch
```

## Database Migration

### Production Database Setup
```bash
# Connect to RDS instance
psql -h <rds-endpoint> -U costwatch_user -d costwatch_db

# Run migrations
./database/init_db.sh --production

# Verify schema
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

### Database Backup Strategy
```bash
# Create automated backup script
cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup_${TIMESTAMP}.sql
aws s3 cp backup_${TIMESTAMP}.sql s3://your-backup-bucket/database/
EOF

# Schedule daily backups
echo "0 2 * * * /path/to/scripts/backup-db.sh" | crontab -
```

## Monitoring Setup

### Prometheus and Grafana
```bash
# Deploy monitoring stack
kubectl apply -f k8s/monitoring/

# Access Grafana dashboard
kubectl port-forward service/grafana 3000:3000 -n costwatch

# Import dashboards
# Browse to http://localhost:3000
# Import dashboards from monitoring/grafana/dashboards/
```

### CloudWatch Integration
```bash
# Install CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cloudwatch-namespace.yaml

# Configure log groups
aws logs create-log-group --log-group-name /aws/eks/costwatch/cluster
```

## SSL/TLS Configuration

### Certificate Management
```bash
# Install cert-manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat > cluster-issuer.yaml << EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourcompany.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: alb
EOF

kubectl apply -f cluster-issuer.yaml
```

## Health Checks and Monitoring

### Application Health Monitoring
```bash
# Create health check script
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash
services=("api-gateway:8000" "cost-analyzer:8001" "resource-scanner:8002" "analytics-engine:8003" "alert-manager:8004")

for service in "${services[@]}"; do
  if curl -f http://$service/health > /dev/null 2>&1; then
    echo "✓ $service is healthy"
  else
    echo "✗ $service is unhealthy"
    exit 1
  fi
done
EOF

chmod +x scripts/health-check.sh
```

### Automated Deployment Verification
```bash
# Deployment verification script
cat > scripts/verify-deployment.sh << 'EOF'
#!/bin/bash
echo "Verifying CostWatch deployment..."

# Check pods are running
kubectl wait --for=condition=ready pod -l app=api-gateway -n costwatch --timeout=300s
kubectl wait --for=condition=ready pod -l app=cost-analyzer -n costwatch --timeout=300s

# Check services are accessible
kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
  curl -f http://api-gateway-service.costwatch:8000/health

echo "Deployment verification complete!"
EOF

chmod +x scripts/verify-deployment.sh
```

## Rollback Procedures

### Application Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/api-gateway -n costwatch
kubectl rollout undo deployment/cost-analyzer -n costwatch

# Check rollback status
kubectl rollout status deployment/api-gateway -n costwatch
```

### Infrastructure Rollback
```bash
# Terraform rollback
cd infrastructure/terraform/environments/prod
terraform plan -destroy -var-file=terraform.tfvars
terraform apply -destroy -var-file=terraform.tfvars
```

## Troubleshooting

### Common Deployment Issues

#### Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs -f deployment/api-gateway -n costwatch

# Check resource limits
kubectl describe pod <pod-name> -n costwatch
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl run db-test --image=postgres:15 --rm -i --restart=Never -- \
  psql -h <rds-endpoint> -U costwatch_user -d costwatch_db -c "SELECT 1;"
```

#### Load Balancer Issues
```bash
# Check ingress status
kubectl describe ingress costwatch-ingress -n costwatch

# Check AWS Load Balancer Controller logs
kubectl logs -f deployment/aws-load-balancer-controller -n kube-system
```

---

This deployment guide provides comprehensive instructions for deploying CostWatch in various environments with proper monitoring and security configurations.