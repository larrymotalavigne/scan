# Scan - Production-Ready Web Application

A modern, production-ready web application built with FastAPI, Angular, and Docker, featuring comprehensive CI/CD, testing, and monitoring capabilities.

## Features

- **Modern Architecture**: 3-layer backend architecture with strict separation of concerns
- **Production Ready**: Docker containers, CI/CD pipeline, comprehensive testing
- **Secure**: Authentication, authorization, security best practices
- **Scalable**: Horizontal scaling, load balancing, caching with Redis
- **Well Documented**: Extensive documentation for development, deployment, and operations

## Tech Stack

### Backend
- **Python 3.12** with **FastAPI** - Modern async web framework
- **PostgreSQL 18** - Robust relational database
- **SQLAlchemy 2.0** - Async ORM for database operations
- **Alembic** - Database migrations
- **Redis 7** - Caching and session storage
- **Pydantic** - Data validation and settings management
- **Pytest** - Comprehensive testing framework

### Frontend
- **Angular 18** - Modern frontend framework with standalone components
- **TypeScript 5** - Type-safe JavaScript
- **PrimeNG** - UI component library
- **RxJS** - Reactive programming
- **Playwright** - End-to-end testing

### Infrastructure
- **Docker** & **Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Nginx** - Reverse proxy and static file serving
- **UV** - Fast Python package installer

## Project Structure

```
scan/
├── back/                          # Backend application
│   ├── api/                       # Main API service
│   │   ├── controllers/           # Business logic layer
│   │   ├── database/              # Data access layer
│   │   ├── views/                 # API routes/endpoints
│   │   ├── schemas/               # Pydantic models
│   │   ├── services/              # External service integrations
│   │   └── main.py                # Application entry point
│   ├── shared/                    # Shared code across services
│   │   ├── core/                  # Config, database, logging
│   │   └── models/                # SQLAlchemy ORM models
│   ├── migrations/                # Database migrations
│   └── tests/                     # Backend test suite
├── front/                         # Frontend application
│   ├── src/app/                   # Angular application
│   │   ├── core/                  # Services, guards, interceptors
│   │   ├── pages/                 # Feature pages
│   │   ├── layout/                # Layout components
│   │   └── shared/                # Reusable components
│   └── e2e/                       # E2E tests
├── docs/                          # Documentation
├── scripts/                       # DevOps scripts
├── config/                        # Configuration files
└── .github/workflows/             # CI/CD pipelines
```

## Architecture

### 3-Layer Backend Architecture

The backend follows a strict 3-layer architecture:

1. **Views Layer** (`*_view.py`): HTTP request/response handling with FastAPI
2. **Controllers Layer** (`*_controller.py`): Business logic (framework-agnostic)
3. **Database Layer** (`*_database.py`): Data access with SQLAlchemy

**Key Principles**:
- No circular dependencies
- Function-based design for simplicity
- Explicit dependency passing
- Type hints throughout
- Async/await for performance

See [Architecture Guidelines](docs/ARCHITECTURE.md) for details.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 22+ (for frontend development)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/scan.git
   cd scan
   ```

2. **Copy environment file**
   ```bash
   cp .env.template .env.development
   # Edit .env.development with your settings
   ```

3. **Start development environment**
   ```bash
   make dev
   ```

4. **Access the application**
   - Frontend: http://localhost:4200
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - API ReDoc: http://localhost:8000/redoc

### Development Setup

#### Backend Development

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install uv
   uv pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   make test
   ```

4. **Run linters**
   ```bash
   make lint
   ```

#### Frontend Development

1. **Install dependencies**
   ```bash
   cd front
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Run tests**
   ```bash
   npm run test:e2e
   ```

### Running Tests

```bash
# All tests
make test

# Unit tests only (fast)
make test-unit

# Integration tests
make test-integration

# With coverage report
make test-cov

# Frontend E2E tests
make test-e2e
```

### Database Migrations

```bash
# Run migrations
make migrate

# Create new migration
make migrate-create

# Downgrade migration
make migrate-downgrade
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example Endpoints

**Create User**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**Get User**
```bash
curl http://localhost:8000/users/1
```

## Production Deployment

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

### Quick Production Deploy

1. **Configure production environment**
   ```bash
   cp .env.template .env.production
   # Edit .env.production with production values
   ```

2. **Build production images**
   ```bash
   make build-prod
   ```

3. **Deploy**
   ```bash
   make deploy
   ```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline:

1. **Lint**: Code quality checks (Ruff, ESLint, MyPy)
2. **Security**: Vulnerability scanning (Trivy)
3. **Test**: Unit, integration, and E2E tests
4. **Build**: Multi-stage Docker builds with caching
5. **Deploy**: Automated deployment to production
6. **Health Check**: Post-deployment verification

See [CI/CD Guide](docs/CI_CD_GUIDE.md) for details.

## Configuration

### Environment Variables

All configuration is managed through environment variables:

- **Application**: `APP_NAME`, `DEBUG`, `SECRET_KEY`
- **Database**: `DATABASE_URL`, `DB_POOL_SIZE`
- **Redis**: `REDIS_URL`
- **Security**: `CORS_ORIGINS`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- **External Services**: `SMTP_HOST`, `SMTP_USER`, etc.

See [.env.template](.env.template) for all available options.

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

### Code Style

- **Backend**: Ruff formatter, type hints required
- **Frontend**: Prettier, ESLint
- **Commits**: Conventional Commits format

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with tests
3. Ensure CI passes
4. Submit PR with description
5. Request review

## Documentation

Comprehensive documentation is available in the `/docs` folder:

- [Architecture Guidelines](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Production Setup](docs/PRODUCTION_SETUP.md)
- [CI/CD Guide](docs/CI_CD_GUIDE.md)
- [Testing Strategy](docs/TESTING_ROADMAP.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## Makefile Commands

Common development tasks:

```bash
make help              # Show all available commands
make install           # Install all dependencies
make dev              # Start development environment
make test             # Run all tests
make lint             # Run linters
make format           # Format code
make migrate          # Run database migrations
make clean            # Clean up containers and volumes
make logs             # Show service logs
make shell-api        # Open shell in API container
make deploy           # Deploy to production
```

## Monitoring and Logging

- **Structured Logging**: JSON logs with request IDs
- **Health Checks**: `/health` endpoint for all services
- **Metrics**: Custom middleware for request tracking
- **Alerting**: Integration with Slack/Discord

## Security

- **Password Hashing**: Bcrypt with automatic salt
- **JWT Authentication**: Secure token-based auth
- **CORS**: Configurable allowed origins
- **Security Headers**: X-Frame-Options, CSP, etc.
- **Dependency Scanning**: Automated vulnerability checks
- **Container Scanning**: Trivy security scans

## Performance

- **Async/Await**: Non-blocking I/O throughout
- **Connection Pooling**: Database and Redis pooling
- **Caching**: Redis for session and data caching
- **CDN Ready**: Static assets with cache headers
- **Horizontal Scaling**: Stateless API design

## License

[Your License Here]

## Support

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/scan/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/scan/discussions)

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Angular](https://angular.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-11
