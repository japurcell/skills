# Project Instructions

Python Django + React TypeScript application.

## Build & Test

- Full build: `make build`
- All tests: `make test`
- Lint: `make lint`
- Backend only: `pip install -r requirements.txt`
- Frontend only: `cd frontend && npm install && npm run build`

## Git Workflow

- Branch naming: feature/, bugfix/, hotfix/
- PR required, at least one review
- Squash merge to develop, merge commit to main
- Conventional commits: `type(scope): description`

## CI/CD

- GitHub Actions
- Pipeline: lint → test → build → deploy
- Deploy to staging on PR merge to develop
- Deploy to production on tag push
- Rollback: revert the tag and redeploy

## Testing Standards

- Minimum 80% coverage on new code
- Mock external services in tests
- Parameterize tests where possible
- E2E: Playwright

## Environment

- Use `.env` with django-environ
- Required: DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS
- Optional: DEBUG (default False), LOG_LEVEL (default WARNING)
- Never commit .env or secrets
- Keep dependencies updated (dependabot enabled)
- Use HTTPS everywhere in production

See [src/backend/AGENTS.md](src/backend/AGENTS.md) for Python, Django, API, and database conventions.
See [src/frontend/AGENTS.md](src/frontend/AGENTS.md) for React and TypeScript conventions.
