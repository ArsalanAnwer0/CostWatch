# Changelog

All notable changes to the CostWatch project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-stage Docker builds for all 5 microservices to reduce image size
- Python 3.11 upgrade across all services for performance improvements
- Comprehensive Terraform backend configuration with S3 and DynamoDB
- Environment-specific tfvars files (dev, staging, production)
- Standardized port assignments across all services (8000-8004)
- Database performance indexes for time-series and JSONB queries
- Database constraints and validation rules for data integrity
- Database views for common queries (monthly costs, active resources, etc.)
- Comprehensive Prometheus alert rules for services, database, and business metrics
- Health monitoring scripts (health-monitor.py, service-monitor.sh)
- PostgreSQL, Redis, and NGINX exporter scrape configs in Prometheus
- Kubernetes secrets template with security best practices
- Startup probes to all Kubernetes deployments for slow-starting apps
- Pytest configuration with 70% coverage threshold
- .dockerignore files to all services
- python-dotenv dependency to cost-analyzer service

### Changed
- Replaced hardcoded JWT secrets with environment variable validation
- Implemented bcrypt password hashing with strength validation
- Fixed CORS configuration to use environment-specific origins
- Updated Kubernetes deployments with proper security contexts
- Fixed duplicate __init__ method in AlertEngine
- Improved JSON serialization of alert metadata (str() to json.dumps())
- Updated port references in Prometheus scrape configs

### Fixed
- Port inconsistencies between Dockerfiles, Kubernetes manifests, and application code
- Kubernetes service definitions now match standardized ports

### Security
- Removed hardcoded secrets (JWT, AWS credentials, database passwords)
- Added runAsNonRoot and capability dropping to all Kubernetes pods
- Implemented proper password hashing with bcrypt
- Configured environment-specific CORS origins
- Added comprehensive secrets management documentation

## [0.1.0] - Initial Release

### Added
- Core microservices architecture with 5 services:
  - API Gateway (port 8002)
  - Cost Analyzer (port 8001)
  - Resource Scanner (port 8000)
  - Analytics Engine (port 8003)
  - Alert Manager (port 8004)
- Terraform infrastructure modules for AWS (VPC, EKS, RDS, IAM, Monitoring)
- Kubernetes manifests for all services
- PostgreSQL database with comprehensive schema
- Prometheus and Grafana monitoring stack
- CI/CD pipeline with GitHub Actions
- Basic frontend with React

### Architecture
- Microservices deployed on Amazon EKS
- PostgreSQL for relational data storage
- Redis for caching and session management
- AWS Cost Explorer integration
- CloudWatch metrics collection
- S3 for report storage
- SNS/SES for alert notifications

---

## Release Notes

### Version 0.2.0 (Upcoming)

**Breaking Changes:**
- Port assignments have been standardized. Update any external integrations:
  - Resource Scanner: 5000 → 8000
  - API Gateway: 8000 → 8002
  - Analytics Engine: 5002 → 8003
  - Alert Manager: 5001 → 8004

**Migration Guide:**
1. Update Kubernetes ConfigMaps with new port values
2. Update any hardcoded service URLs in client applications
3. Re-deploy all services with new Docker images
4. Verify Prometheus scrape targets are collecting metrics

**Security Updates:**
- All services now require proper environment variable configuration
- JWT_SECRET_KEY must be set via Kubernetes secrets
- DATABASE_PASSWORD must be configured securely
- AWS credentials should use IAM roles (IRSA) instead of static keys

**Database Updates:**
- Apply new performance indexes: `psql < database/schemas/04_performance_indexes.sql`
- Apply new constraints: `psql < database/schemas/05_constraints.sql`
- Apply new views: `psql < database/schemas/06_views.sql`

**Infrastructure:**
- Initialize Terraform backend: `terraform init -backend-config=environments/<env>/backend.hcl`
- Create S3 bucket for state: `aws s3 mb s3://costwatch-terraform-state-<env>`
- Create DynamoDB table: See `infrastructure/terraform/backend.tf` for instructions

---

## Contributing

When adding entries to this changelog:
1. Add unreleased changes to the `[Unreleased]` section
2. Use the categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Link to relevant issues or pull requests
4. Keep descriptions concise and user-focused
5. Move items to a release section when publishing a new version

## Links
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [CostWatch Repository](https://github.com/your-org/costwatch)
