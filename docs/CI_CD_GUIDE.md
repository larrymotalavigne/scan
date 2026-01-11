# CI/CD Guide

Documentation for the GitHub Actions CI/CD pipeline.

## Pipeline Overview

The CI/CD pipeline consists of 6 stages:

1. **Lint**: Code quality checks
2. **Security**: Vulnerability scanning
3. **Test**: Unit, integration, and E2E tests
4. **Build**: Docker image building and pushing
5. **Deploy**: Automated deployment to production
6. **Health Check**: Post-deployment verification

## Pipeline Stages

### Stage 1: Lint (Parallel)

**Backend Linting**:
- Ruff: Code style and quality
- MyPy: Static type checking
- Runs on every push and PR

**Frontend Linting**:
- ESLint: Code quality
- Prettier: Code formatting
- Runs on every push and PR

### Stage 2: Security Scanning

- **Trivy**: Vulnerability scanning for dependencies and Docker images
- Results uploaded to GitHub Security tab
- Fails on CRITICAL and HIGH vulnerabilities

### Stage 3: Testing

**Backend Tests**:
- Unit tests with pytest
- Integration tests with real PostgreSQL and Redis
- Coverage reporting to Codecov
- Minimum 70% coverage required

**Frontend Tests**:
- E2E tests with Playwright
- Multiple browsers (Chrome, Firefox, Safari)
- Visual regression testing

### Stage 4: Build and Push

- Multi-stage Docker builds
- Pushes to GitHub Container Registry
- Tags: branch name, commit SHA, semver, latest
- BuildKit caching for faster builds

### Stage 5: Deploy (Production Only)

- Runs only on `main` branch
- SSH deployment to production server
- Database migrations
- Rolling updates for zero downtime
- Automatic rollback on failure

### Stage 6: Health Check

- Verifies API and frontend endpoints
- Slack/Discord notifications on failure
- Runs after successful deployment

## Secrets Configuration

Required GitHub Secrets:

```
PRODUCTION_HOST        # Production server IP/hostname
PRODUCTION_USER        # SSH username
PRODUCTION_SSH_KEY     # Private SSH key for deployment
SLACK_WEBHOOK         # Slack webhook URL (optional)
CODECOV_TOKEN         # Codecov upload token (optional)
```

### Setting up Secrets

1. Go to repository Settings → Secrets → Actions
2. Add each required secret
3. Use `Repository secrets` for production, `Environment secrets` for staging

## Triggering Workflows

### Automatic Triggers

- **Push to `main`**: Full pipeline + deployment
- **Push to `develop`**: Full pipeline without deployment
- **Push to `claude/**`**: Full pipeline without deployment
- **Pull Request to `main`**: Full pipeline without deployment

### Manual Triggers

```bash
# Trigger via GitHub CLI
gh workflow run ci-cd.yml --ref main

# Or use GitHub UI: Actions → CI/CD Pipeline → Run workflow
```

## Environment-Specific Deployments

### Development

```yaml
on:
  push:
    branches: [develop]

deploy-dev:
  environment:
    name: development
    url: https://dev.example.com
```

### Staging

```yaml
on:
  pull_request:
    branches: [main]

deploy-staging:
  environment:
    name: staging
    url: https://staging.example.com
```

### Production

```yaml
on:
  push:
    branches: [main]

deploy:
  environment:
    name: production
    url: https://example.com
```

## Deployment Process

### Successful Deployment Flow

1. **Code pushed to main**
2. **Lint and security checks pass**
3. **All tests pass**
4. **Docker images built and pushed**
5. **SSH to production server**
6. **Pull latest images**
7. **Run database migrations**
8. **Rolling update services**
9. **Health checks pass**
10. **Success notification**

### Failed Deployment Flow

1. **Health check fails**
2. **Automatic rollback triggered**
3. **Previous version restored**
4. **Failure notification sent**

## Monitoring Pipeline

### View Pipeline Status

```bash
# Using GitHub CLI
gh run list --workflow=ci-cd.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Pipeline Metrics

- Average build time: ~15 minutes
- Average test time: ~5 minutes
- Average deploy time: ~10 minutes
- Success rate target: >95%

## Optimizing Pipeline

### Caching

```yaml
# Python dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}

# Node modules
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# Docker layers
cache-from: type=gha
cache-to: type=gha,mode=max
```

### Parallel Jobs

Run independent jobs in parallel:

```yaml
jobs:
  lint-backend:
    runs-on: ubuntu-latest
  lint-frontend:
    runs-on: ubuntu-latest
  security-scan:
    runs-on: ubuntu-latest
```

## Troubleshooting

### Common Issues

**1. Tests Failing**

```bash
# Run tests locally
make test

# Check logs in GitHub Actions
gh run view <run-id> --log
```

**2. Build Failing**

```bash
# Build locally
docker compose -f docker-compose.prod.yml build

# Check Dockerfile syntax
docker build -t test -f back/Dockerfile.prod .
```

**3. Deployment Failing**

```bash
# Check server connectivity
ssh production-server

# Verify environment variables
cat /opt/scan/.env.production

# Check Docker on server
docker ps
docker compose -f docker-compose.prod.yml ps
```

**4. Security Scan Failing**

```bash
# Run Trivy locally
docker run --rm -v $(PWD):/app aquasec/trivy fs /app

# Update dependencies
pip install --upgrade -r requirements.txt
```

## Best Practices

1. **Always run tests locally before pushing**
2. **Use feature branches for development**
3. **Squash commits before merging to main**
4. **Write descriptive commit messages**
5. **Monitor pipeline execution times**
6. **Review security scan results**
7. **Keep dependencies up to date**
8. **Test rollback procedures regularly**

## Advanced Configuration

### Matrix Builds

Build multiple versions in parallel:

```yaml
strategy:
  matrix:
    python-version: [3.11, 3.12]
    node-version: [20, 22]
```

### Conditional Deployment

```yaml
deploy:
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### Custom Runners

Use self-hosted runners for faster builds:

```yaml
runs-on: [self-hosted, linux, x64]
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
