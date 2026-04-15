# Project Instructions

This is a Python Django application with a React frontend.
See [src/backend/AGENTS.md](src/backend/AGENTS.md) and [src/frontend/AGENTS.md](src/frontend/AGENTS.md) for domain-specific rules.

## Build Commands

- Full build: `make build`
- Tests: `make test`
- Lint: `make lint`

## Package Managers

- Backend: pip with requirements.txt
- Frontend: npm with package-lock.json

## Testing Strategy

- Minimum 80% coverage on new code
- Mock external services in tests
- Use factory_boy for test data generation
- Parameterize tests where possible
- E2E: Playwright

## Environment

- Use .env with django-environ
- Required: DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS
- Optional: DEBUG (default False), LOG_LEVEL (default WARNING)
- Never commit .env or secrets

## CI/CD

- GitHub Actions
- Pipeline: lint → test → build → deploy
- Deploy to staging on PR merge to develop
- Deploy to production on tag push
- Rollback: revert the tag and redeploy

## Git Workflow

- Branch naming: feature/, bugfix/, hotfix/
- PR required, at least one review
- Squash merge to develop, merge commit to main
- Conventional commits: type(scope): description

## Logging

- Use structlog for structured logging
- JSON format in production, console format in development
- Always include request_id in log context
- Log all exceptions with full traceback
- Use appropriate log levels: DEBUG for development, INFO for happy path, WARNING for recoverable issues, ERROR for failures

## Security

- Run bandit for security linting
- Keep dependencies updated (dependabot enabled)
- Use parameterized queries (ORM handles this)
- Validate all user input server-side
- Set CSRF and CORS headers appropriately
- Use HTTPS everywhere in production
