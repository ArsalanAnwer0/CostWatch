# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of CostWatch seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Disclose Publicly

Please do not open a public GitHub issue for security vulnerabilities. This helps protect users while we work on a fix.

### 2. Report via Email

Send details to: **security@costwatch.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical issues within 30 days

### 4. Disclosure Policy

- We will acknowledge your report within 48 hours
- We will keep you informed of our progress
- We will credit you in release notes (unless you prefer anonymity)
- We will coordinate public disclosure after a fix is available

---

## Security Best Practices

### Authentication & Authorization

**JWT Token Management:**
```bash
# Generate secure JWT secret (minimum 256 bits)
openssl rand -base64 32

# Set in Kubernetes secret
kubectl create secret generic costwatch-secrets \
  --from-literal=JWT_SECRET_KEY="your-generated-secret" \
  -n costwatch
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Hashed with bcrypt (cost factor 12)

**API Key Security:**
- Rotate API keys every 90 days
- Store hashed versions only
- Use separate keys per environment
- Implement rate limiting per key

### Infrastructure Security

**Kubernetes Security:**
```yaml
# All pods run as non-root
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

# Containers drop all capabilities
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false
  capabilities:
    drop:
      - ALL
```

**Network Policies:**
- Implement zero-trust networking
- Restrict pod-to-pod communication
- Allow only necessary ingress/egress
- Use NetworkPolicies for isolation

**RBAC Configuration:**
```bash
# Principle of least privilege
# Grant minimum necessary permissions
kubectl create serviceaccount costwatch-sa -n costwatch
kubectl create rolebinding costwatch-binding \
  --role=costwatch-role \
  --serviceaccount=costwatch:costwatch-sa
```

### Secrets Management

**Kubernetes Secrets:**
```bash
# Never commit secrets to Git
# Use sealed-secrets or External Secrets Operator

# Example with External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: costwatch-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: costwatch-secrets
  data:
  - secretKey: DATABASE_PASSWORD
    remoteRef:
      key: costwatch/prod/database
      property: password
```

**AWS IAM Roles for Service Accounts (IRSA):**
```bash
# Preferred over static credentials
eksctl create iamserviceaccount \
  --name costwatch-sa \
  --namespace costwatch \
  --cluster costwatch-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/AWSCostExplorerReadOnlyAccess \
  --approve
```

**Secret Rotation:**
- Database passwords: Every 90 days
- API keys: Every 90 days
- JWT secrets: Every 180 days
- TLS certificates: Before expiration

### Database Security

**Connection Security:**
```bash
# Always use SSL/TLS for database connections
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"

# Use connection pooling with limits
MAX_CONNECTIONS=10
POOL_TIMEOUT=30
```

**Access Control:**
```sql
-- Principle of least privilege
GRANT SELECT, INSERT, UPDATE ON cost_data TO costwatch_user;
REVOKE DELETE ON cost_data FROM costwatch_user;

-- Use row-level security
ALTER TABLE cost_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_isolation ON cost_data
  USING (organization_id = current_setting('app.current_org_id')::uuid);
```

**Data Encryption:**
- Encryption at rest: Enable on RDS/Aurora
- Encryption in transit: Require SSL connections
- Backup encryption: Enable automatic encryption

### Application Security

**Input Validation:**
```python
# Validate all user inputs
from pydantic import BaseModel, validator

class CostQuery(BaseModel):
    organization_id: UUID
    start_date: date
    end_date: date

    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
```

**SQL Injection Prevention:**
```python
# Always use parameterized queries
cursor.execute(
    "SELECT * FROM cost_data WHERE organization_id = %s",
    (org_id,)
)

# NEVER concatenate SQL strings
# BAD: f"SELECT * FROM cost_data WHERE org_id = '{org_id}'"
```

**XSS Prevention:**
```python
# Sanitize all outputs
from html import escape

def safe_render(user_input: str) -> str:
    return escape(user_input)
```

**CORS Configuration:**
```python
# Environment-specific origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

# NEVER use wildcard in production
# BAD: allow_origins=["*"]
# GOOD: allow_origins=["https://app.costwatch.com"]
```

**Rate Limiting:**
```python
# Implement per-IP and per-user rate limits
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/costs")
@limiter.limit("100/hour")
async def get_costs():
    pass
```

### Monitoring & Logging

**Security Audit Logging:**
```python
# Log all authentication attempts
logger.info(
    "Authentication attempt",
    extra={
        "user": username,
        "ip": request.client.host,
        "success": auth_success,
        "timestamp": datetime.utcnow()
    }
)
```

**Sensitive Data Masking:**
```python
# Never log passwords, tokens, or secrets
logger.info(f"User login: {username}")  # Good
# logger.info(f"Login: {username}:{password}")  # BAD
```

**Intrusion Detection:**
- Monitor failed authentication attempts
- Alert on unusual API usage patterns
- Track privilege escalation attempts
- Monitor file integrity changes

### Dependency Management

**Regular Updates:**
```bash
# Update dependencies monthly
pip list --outdated
pip install --upgrade package-name

# Check for vulnerabilities
pip-audit
safety check
```

**Container Scanning:**
```bash
# Scan Docker images for vulnerabilities
trivy image costwatch/api-gateway:latest
docker scan costwatch/api-gateway:latest
```

**Automated Security Checks:**
```yaml
# GitHub Actions security workflow
- name: Run security scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'costwatch/api-gateway:latest'
    severity: 'CRITICAL,HIGH'
```

### Compliance & Data Protection

**GDPR Compliance:**
- Implement right to erasure (soft delete with `deleted_at`)
- Provide data export functionality
- Document data retention policies
- Implement consent management

**Data Retention:**
```sql
-- Automatically delete old data
DELETE FROM cost_data
WHERE cost_date < NOW() - INTERVAL '2 years'
AND organization_id IN (
  SELECT id FROM organizations WHERE data_retention_days = 730
);
```

**Audit Trails:**
```sql
-- Track all data modifications
CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  table_name VARCHAR(100),
  operation VARCHAR(10),
  user_id UUID,
  changes JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Incident Response

**Security Incident Playbook:**

1. **Detection**: Monitor alerts, logs, and user reports
2. **Containment**: Isolate affected systems
3. **Investigation**: Gather evidence and analyze impact
4. **Eradication**: Remove threat and patch vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve processes

**Emergency Contacts:**
- Security Team: security@costwatch.com
- On-Call Engineer: Use PagerDuty escalation
- Legal Team: legal@costwatch.com

---

## Security Checklist for Production

### Pre-Deployment

- [ ] All secrets stored in Kubernetes Secrets or AWS Secrets Manager
- [ ] TLS certificates installed and valid
- [ ] Security contexts configured on all pods
- [ ] Network policies implemented
- [ ] RBAC roles and bindings configured
- [ ] Database encryption at rest enabled
- [ ] Database SSL connections required
- [ ] API rate limiting enabled
- [ ] CORS origins properly configured
- [ ] Security audit logging enabled
- [ ] Container images scanned for vulnerabilities
- [ ] Dependencies checked for known CVEs
- [ ] Backup and disaster recovery tested

### Post-Deployment

- [ ] Security monitoring alerts configured
- [ ] Intrusion detection active
- [ ] Log aggregation working
- [ ] Automated vulnerability scanning running
- [ ] Incident response plan documented
- [ ] Security training completed for team
- [ ] Penetration testing scheduled
- [ ] Compliance audit completed

---

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

## Contact

For security concerns, contact: **security@costwatch.com**
