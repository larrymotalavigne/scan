.PHONY: help install dev up down build test lint format clean migrate deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make dev          - Start development environment"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make build        - Build Docker images"
	@echo "  make build-prod   - Build production Docker images"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migrate-create - Create new migration"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make logs         - Show service logs"
	@echo "  make shell-api    - Open shell in API container"
	@echo "  make shell-db     - Open PostgreSQL shell"
	@echo "  make deploy       - Deploy to production"

# Installation
install:
	@echo "Installing backend dependencies..."
	pip install uv
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd front && npm install
	@echo "Installation complete!"

# Development
dev: up
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:4200"
	@echo "API Docs: http://localhost:8000/docs"

up:
	docker compose up -d

down:
	docker compose down

# Build
build:
	docker compose build

build-prod:
	docker compose -f docker-compose.prod.yml build

# Testing
test:
	. .venv/bin/activate && pytest

test-unit:
	. .venv/bin/activate && pytest -m unit

test-integration:
	. .venv/bin/activate && pytest -m integration

test-cov:
	. .venv/bin/activate && pytest --cov --cov-report=html
	@echo "Coverage report available at htmlcov/index.html"

test-e2e:
	cd front && npm run test:e2e

# Linting and Formatting
lint:
	@echo "Linting backend..."
	. .venv/bin/activate && ruff check back/
	. .venv/bin/activate && mypy back/api back/shared
	@echo "Linting frontend..."
	cd front && npm run lint

format:
	@echo "Formatting backend..."
	. .venv/bin/activate && ruff format back/
	@echo "Formatting frontend..."
	cd front && npm run format

# Database
migrate:
	docker compose exec api alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker compose exec api alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	docker compose exec api alembic downgrade -1

# Utilities
clean:
	docker compose down -v
	rm -rf .venv htmlcov .pytest_cache .ruff_cache .mypy_cache
	cd front && rm -rf node_modules dist .angular

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-frontend:
	docker compose logs -f frontend

shell-api:
	docker compose exec api /bin/bash

shell-db:
	docker compose exec database psql -U postgres -d scan

shell-redis:
	docker compose exec redis redis-cli

# Production
deploy:
	@echo "Deploying to production..."
	./scripts/deploy.sh

deploy-rollback:
	@echo "Rolling back deployment..."
	./scripts/rollback.sh

# Backup
backup:
	@echo "Creating backup..."
	./scripts/backup.sh

# Security
security-scan:
	@echo "Running security scans..."
	. .venv/bin/activate && bandit -r back/
	. .venv/bin/activate && safety check
	docker run --rm -v $(PWD):/app aquasec/trivy fs /app

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "✓ API is healthy" || echo "✗ API is down"
	@curl -f http://localhost:4200/health && echo "✓ Frontend is healthy" || echo "✗ Frontend is down"

# Database backup and restore
db-backup:
	@echo "Backing up database..."
	docker compose exec database pg_dump -U postgres scan > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up successfully"

db-restore:
	@read -p "Enter backup file path: " file; \
	docker compose exec -T database psql -U postgres scan < $$file

# Container inspection
ps:
	docker compose ps

stats:
	docker stats

# Frontend specific
frontend-build:
	cd front && npm run build:prod

frontend-serve:
	cd front && npm start
