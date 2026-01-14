# Contributing to CostWatch

Thank you for your interest in contributing to CostWatch! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or trolling
- Publishing others' private information
- Spam or excessive self-promotion
- Other conduct inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for frontend)
- **Docker & Docker Compose**
- **Kubernetes (minikube or kind for local development)**
- **Terraform 1.0+**
- **Git**
- **AWS CLI** (configured with appropriate credentials)

### Finding Issues

1. Browse [open issues](https://github.com/your-org/costwatch/issues)
2. Look for issues tagged `good-first-issue` or `help-wanted`
3. Comment on an issue to express interest before starting work

### Claiming an Issue

```
I'd like to work on this issue. My approach would be:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected timeline: [X days]
```

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/costwatch.git
cd costwatch

# Add upstream remote
git remote add upstream https://github.com/your-org/costwatch.git
```

### 2. Environment Setup

```bash
# Run automated setup script
./scripts/setup.sh

# Or manual setup:
# Create virtual environment for each service
cd services/api-gateway
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# Minimum required:
export DATABASE_URL="postgresql://localhost:5432/costwatch_dev"
export JWT_SECRET_KEY="your-dev-secret-key"
export AWS_REGION="us-west-2"
```

### 4. Start Local Services

```bash
# Start infrastructure (PostgreSQL, Redis)
docker-compose up -d postgres redis

# Run database migrations
psql -U postgres -d costwatch_dev -f database/schemas/01_init.sql
psql -U postgres -d costwatch_dev -f database/schemas/02_tables.sql
psql -U postgres -d costwatch_dev -f database/schemas/03_seed_data.sql

# Start a service
cd services/api-gateway
uvicorn app.main:app --reload --port 8002
```

### 5. Verify Installation

```bash
# Check service health
curl http://localhost:8002/health

# Run tests
pytest services/api-gateway/tests/ -v
```

---

## Development Workflow

### Branch Naming

```
feature/add-cost-forecasting
fix/auth-token-expiry
refactor/database-queries
docs/api-reference-update
test/integration-cost-analyzer
```

### Workflow Steps

```bash
# 1. Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit frequently
git add .
git commit -m "feat(scope): description"

# 4. Keep branch updated
git fetch upstream
git rebase upstream/main

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Open Pull Request on GitHub
```

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

```python
# Good
def calculate_monthly_costs(
    organization_id: UUID,
    start_date: date,
    end_date: date
) -> Decimal:
    """
    Calculate total costs for an organization in a date range.

    Args:
        organization_id: The organization's unique identifier
        start_date: Start of the date range (inclusive)
        end_date: End of the date range (inclusive)

    Returns:
        Total cost as a Decimal

    Raises:
        ValueError: If end_date is before start_date
    """
    if end_date < start_date:
        raise ValueError("end_date must be after start_date")

    query = """
        SELECT SUM(unblended_cost)
        FROM cost_data
        WHERE organization_id = %s
        AND cost_date BETWEEN %s AND %s
    """
    return execute_query(query, (organization_id, start_date, end_date))
```

### Linting and Formatting

```bash
# Format code with black
black services/api-gateway/app/

# Sort imports with isort
isort services/api-gateway/app/

# Check with flake8
flake8 services/api-gateway/app/

# Type check with mypy
mypy services/api-gateway/app/
```

### TypeScript/React Style

```typescript
// Good
interface CostData {
  organizationId: string;
  totalCost: number;
  currency: string;
  period: DateRange;
}

const CostDashboard: React.FC = () => {
  const [costs, setCosts] = useState<CostData[]>([]);

  useEffect(() => {
    const fetchCosts = async () => {
      const data = await costService.getMonthlyCosts();
      setCosts(data);
    };

    fetchCosts();
  }, []);

  return (
    <div className="cost-dashboard">
      {costs.map(cost => (
        <CostCard key={cost.organizationId} data={cost} />
      ))}
    </div>
  );
};
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```
feat(api-gateway): add rate limiting middleware

Implements Redis-based rate limiting with configurable
limits per endpoint. Defaults to 100 requests per hour.

Closes #123

---

fix(cost-analyzer): handle null values in cost calculations

Previously threw exception when costs were null.
Now treats null as zero and logs a warning.

Fixes #456
```

---

## Testing Guidelines

### Test Structure

```
services/api-gateway/tests/
├── unit/
│   ├── test_auth.py
│   └── test_cost_calculator.py
├── integration/
│   ├── test_database.py
│   └── test_external_apis.py
└── e2e/
    └── test_full_workflow.py
```

### Writing Unit Tests

```python
import pytest
from app.services.cost_calculator import CostCalculator

class TestCostCalculator:
    @pytest.fixture
    def calculator(self):
        return CostCalculator()

    def test_calculate_daily_cost(self, calculator):
        """Test daily cost calculation with valid data"""
        result = calculator.calculate_daily_cost(
            service_type="ec2",
            instance_hours=24,
            hourly_rate=0.10
        )
        assert result == 2.40

    def test_calculate_daily_cost_invalid_hours(self, calculator):
        """Test that invalid hours raises ValueError"""
        with pytest.raises(ValueError, match="hours must be positive"):
            calculator.calculate_daily_cost(
                service_type="ec2",
                instance_hours=-1,
                hourly_rate=0.10
            )
```

### Test Coverage Requirements

- **Minimum**: 70% overall coverage
- **New code**: 80% coverage required
- **Critical paths**: 90% coverage (auth, billing)

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```python
@pytest.mark.integration
def test_database_connection():
    """Test that database connection works"""
    conn = get_db_connection()
    assert conn is not None

    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation
- [ ] No merge conflicts with main
- [ ] Commit messages follow convention

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows code style guidelines

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, security scans
2. **Code Review**: At least 1 approval required
3. **Testing**: QA team tests in staging environment
4. **Approval**: Maintainer approves for merge

### Addressing Feedback

```bash
# Make requested changes
git add .
git commit -m "refactor: address review feedback"

# Push updates
git push origin feature/your-feature-name
```

---

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. Update CHANGELOG.md
2. Update version in setup.py
3. Tag release: `git tag v1.2.3`
4. Build Docker images
5. Run full test suite
6. Deploy to staging
7. Deploy to production
8. Create GitHub release with notes

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Slack**: Real-time collaboration (get invite from maintainers)

### Getting Help

- Check documentation in `/docs`
- Search existing issues
- Ask in GitHub Discussions
- Reach out in Slack

### Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- Contributors section in README
- Annual contributor highlights

---

## Additional Resources

- [Architecture Overview](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Security Guidelines](./SECURITY.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

Thank you for contributing to CostWatch! 🚀
