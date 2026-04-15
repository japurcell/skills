# Backend Instructions

Django REST Framework backend — Python 3.11+.

## Build & Test

- Install: `pip install -r requirements.txt`
- Tests: `pytest` (uses pytest-django)
- Integration tests: pytest with Django test client
- Test data: factory_boy
- Lint: `make lint`

## Python Style

- Type hints on all public functions
- Use dataclasses for DTOs, Pydantic for request/response validation
- Follow PEP 8; format with Black, sort imports with isort
- Docstrings on all public modules, classes, and functions
- Use pathlib over os.path, f-strings over `.format()`
- Context managers for file operations
- Never use bare except clauses

## Django Conventions

- Apps in src/backend/apps/
- Class-based views for CRUD, function-based for custom logic
- Always use DRF serializers for API responses
- Custom permissions in permissions.py per app
- Signals registered in apps.py `ready()` method
- Use select_related/prefetch_related to avoid N+1 queries
- Custom management commands in management/commands/
- Fixtures in fixtures/ directory per app

## Database

- PostgreSQL
- Create migrations: `python manage.py makemigrations`
- Run migrations: `python manage.py migrate`
- Never edit migration files after merge to main
- Use Django ORM; no raw SQL unless performance-critical

## API Design

- RESTful endpoints under /api/v1/
- Use DRF viewsets for standard CRUD
- Token auth via DRF TokenAuthentication
- Rate limit public endpoints with django-ratelimit
- Paginated responses for list endpoints
- DRF filtering backends for query params
- All endpoints must have OpenAPI schema decorators

## Logging

- structlog with JSON format (production) / console format (development)
- Always include request_id in log context
- Log all exceptions with full traceback
- Levels: DEBUG dev, INFO happy path, WARNING recoverable, ERROR failures

## Security

- Run bandit for security linting
- Parameterized queries (ORM handles this)
- Validate all user input server-side
- Set CSRF and CORS headers appropriately
