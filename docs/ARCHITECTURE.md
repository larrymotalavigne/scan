# Architecture Documentation

## Overview

Scan is built with a modern monorepo architecture featuring strict separation of concerns, type safety, and production-ready patterns.

## Architecture Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Function Over Class**: Pure functions for simplicity and testability
3. **Explicit Over Implicit**: No magic, all dependencies explicit
4. **Type Safety**: Type hints throughout Python and TypeScript
5. **Async by Default**: Non-blocking I/O for performance

## Backend Architecture

### 3-Layer Pattern

```
┌─────────────────────────────────────────┐
│           Views Layer                    │
│  (HTTP request/response handling)        │
│  - FastAPI routers                       │
│  - Dependency injection                  │
│  - Request validation                    │
│  - Error handling                        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│        Controllers Layer                 │
│      (Business logic)                    │
│  - Framework-agnostic                    │
│  - Business rules                        │
│  - Orchestration                         │
│  - Transaction management                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Database Layer                   │
│        (Data access)                     │
│  - SQLAlchemy queries                    │
│  - CRUD operations                       │
│  - NO business logic                     │
│  - NO external calls                     │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

**Views (`*_view.py`)**:
- HTTP concerns only
- Request/response handling
- Dependency injection (database, services)
- Call controller functions
- Return HTTP responses

**Controllers (`*_controller.py`)**:
- Business logic
- Validation rules
- Orchestrate database and services
- Framework-agnostic pure functions
- Return domain objects

**Database (`*_database.py`)**:
- SQLAlchemy queries only
- Accept AsyncSession as parameter
- Return models or None
- NO business logic
- NO external service calls

### Example Flow

User Creation Flow:

```python
# 1. View receives request
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 2. Call controller
    user = await user_controller.create_user(db, user_data)
    # 3. Return response
    return UserResponse.model_validate(user)

# 4. Controller orchestrates business logic
async def create_user(db: AsyncSession, user_data: UserCreate):
    # Business rule: check email uniqueness
    existing = await user_database.get_user_by_email(db, user_data.email)
    if existing:
        raise ValueError("Email already registered")

    # Business rule: hash password
    hashed_password = get_password_hash(user_data.password)

    # 5. Database performs data access
    return await user_database.create_user(db, user_data, hashed_password)

# 6. Database executes query
async def create_user(db: AsyncSession, user_data: UserCreate, hashed_password: str):
    user = User(**user_data.model_dump(), hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
```

## Frontend Architecture

### Component Structure

```
app/
├── core/                    # Singleton services
│   ├── services/            # Global services
│   ├── guards/              # Route guards
│   ├── interceptors/        # HTTP interceptors
│   └── interfaces/          # TypeScript interfaces
├── pages/                   # Feature routes
│   └── home/
│       ├── home.component.ts
│       ├── home.component.html
│       └── home.component.scss
├── layout/                  # Shell components
│   ├── header/
│   ├── footer/
│   └── sidebar/
└── shared/                  # Reusable components
    ├── components/
    └── directives/
```

### Angular Patterns

- **Standalone Components**: No NgModules
- **Signal-based Reactivity**: Modern state management
- **Functional Guards**: Route protection
- **Lazy Loading**: Route-level code splitting
- **RxJS**: Async operations and state

## Database Schema

### Core Models

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### Migrations

Using Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Infrastructure

### Docker Architecture

**Development**:
- Hot reload for backend and frontend
- Volume mounts for code
- Debug mode enabled
- Local PostgreSQL and Redis

**Production**:
- Multi-stage builds
- Minimal runtime images
- Non-root users
- Health checks
- Resource limits
- Log rotation

### Container Communication

```
┌─────────────────┐
│     Nginx       │  (Port 80/443)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐ ┌──▼────┐
│  API   │ │ Front │
│ (8000) │ │  (80) │
└───┬────┘ └───────┘
    │
┌───▼────┐ ┌────────┐
│ Postgres│ │ Redis  │
│ (5432) │ │ (6379) │
└────────┘ └────────┘
```

## Security Architecture

### Authentication Flow

```
1. User submits credentials
2. Controller validates against database
3. JWT token generated
4. Token returned to client
5. Client includes token in requests
6. Middleware validates token
7. User context available in request
```

### Security Layers

1. **Input Validation**: Pydantic schemas
2. **Authentication**: JWT tokens
3. **Authorization**: Role-based access control
4. **Password Hashing**: Bcrypt with salt
5. **CORS**: Configured allowed origins
6. **Security Headers**: CSP, X-Frame-Options, etc.
7. **HTTPS**: TLS/SSL in production

## Testing Strategy

### Test Pyramid

```
        /\
       /E2E\        5% - Full user workflows
      /-----\
     / Integ \      25% - Layer interactions
    /--------\
   /   Unit   \     70% - Individual functions
  /___________\
```

### Test Types

**Unit Tests**:
- Pure functions in isolation
- Mock external dependencies
- Fast execution (<100ms)
- High code coverage

**Integration Tests**:
- Layer interactions
- Real database (testcontainers)
- Mock external APIs
- Critical path coverage

**E2E Tests**:
- Full user journeys
- Playwright
- Multiple browsers
- Visual regression

## Performance Optimization

### Backend

1. **Async/Await**: Non-blocking I/O
2. **Connection Pooling**: Database and Redis
3. **Query Optimization**: Eager loading, indexing
4. **Caching**: Redis for sessions and data
5. **Background Jobs**: Celery for long tasks

### Frontend

1. **Lazy Loading**: Route-based code splitting
2. **AOT Compilation**: Ahead-of-time compilation
3. **Tree Shaking**: Remove unused code
4. **CDN**: Static assets cached
5. **Service Workers**: Offline capabilities

## Scalability

### Horizontal Scaling

- **Stateless API**: Multiple replicas
- **Load Balancing**: Nginx or cloud LB
- **Session Storage**: Redis for shared state
- **Database**: Read replicas for scaling reads

### Vertical Scaling

- **Resource Limits**: Configured per service
- **Connection Pools**: Tuned for load
- **Worker Processes**: Multiple Uvicorn workers

## Monitoring and Observability

### Logging

- **Structured Logs**: JSON format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request IDs**: Trace requests across services
- **Log Aggregation**: Centralized logging

### Metrics

- **Health Checks**: /health endpoints
- **Response Times**: Middleware tracking
- **Error Rates**: Automatic error logging
- **Resource Usage**: Container metrics

### Alerting

- **Slack/Discord**: Deployment notifications
- **Email**: Critical errors
- **PagerDuty**: On-call rotation (optional)

## Deployment Architecture

### CI/CD Pipeline

```
Code Push → Lint → Security → Test → Build → Deploy → Health Check
```

### Zero-Downtime Deployment

1. Build new image
2. Pull to production server
3. Run database migrations
4. Start new containers
5. Health check passes
6. Route traffic to new containers
7. Stop old containers
8. Cleanup

## Best Practices

1. **No circular dependencies**
2. **Type hints everywhere**
3. **Async/await throughout**
4. **Function-based design**
5. **Explicit dependency passing**
6. **Comprehensive testing**
7. **Security by default**
8. **Documentation always updated**

## Future Enhancements

- [ ] GraphQL API option
- [ ] WebSocket support
- [ ] Microservices split
- [ ] Kubernetes deployment
- [ ] Service mesh (Istio)
- [ ] Event sourcing
- [ ] CQRS pattern
