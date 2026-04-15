# Backend Instructions

Django REST Framework backend with Python 3.11+.

## Build & Test

- Install: `pip install -r requirements.txt`
- Tests: `pytest` (uses pytest-django)
- Integration tests: pytest with Django test client
- Lint: `make lint`

## Python Style

- Type hints on all public functions
- Use dataclasses for DTOs
- Use Pydantic for request/response validation
- Follow PEP 8
- Use Black for formatting, isort for import sorting
- Docstrings on all public modules, classes, and functions
- Use pathlib over os.path
- Use f-strings over .format()
- Context managers for file operations
- Never use bare except clauses

## Django Conventions

- Apps in src/backend/apps/
- Use class-based views for CRUD, function-based for custom logic
- Always use DRF serializers for API responses
- Custom permissions go in permissions.py per app
- Signals should be registered in apps.py ready() method
- Use select_related and prefetch_related to avoid N+1 queries
- Custom management commands in management/commands/
- Use Django's built-in test client for API tests
- Fixtures in fixtures/ directory per app

## Database

- PostgreSQL
- Always create migrations: `python manage.py makemigrations`
- Run migrations: `python manage.py migrate`
- Never edit migration files after merge to main
- Use Django ORM, no raw SQL unless performance-critical

## API Design

- RESTful endpoints under /api/v1/
- Use DRF viewsets for standard CRUD
- Token auth via DRF TokenAuthentication
- Rate limit all public endpoints with django-ratelimit
- Return paginated responses for list endpoints
- Use DRF filtering backends for query params
- All endpoints must have OpenAPI schema decorators
