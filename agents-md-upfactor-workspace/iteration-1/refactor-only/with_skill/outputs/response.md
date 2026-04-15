# AGENTS.md Refresh — Results

## A. Contradictions Found

**1. Accessible forms — missing "error messages" in frontend file**
- **Root AGENTS.md**: "All forms need accessible labels and error messages"
- **src/frontend/AGENTS.md**: "All forms need accessible labels"
- **Resolution**: Kept the more complete version ("labels and error messages") in the frontend file, since that's the authoritative location going forward.

No other conflicts found.

## B. New Learnings

No new learnings to add — the user confirmed there are no session-specific discoveries to capture.

## C. Structural Changes

### Problems found in original structure
| Signal | Detail |
|--------|--------|
| Root too long | 125 lines (limit ~120) |
| Duplication | Frontend AGENTS.md duplicated 9 of 10 root React rules verbatim |
| Duplication | Backend AGENTS.md duplicated 6 Django rules + 4 Python style rules from root |
| Mixed scopes | Root contained domain-specific Python style, Django, React, API, logging, and security rules |
| Missing links | Root had no cross-references to subdirectory files |

### Proposed structure

```
AGENTS.md                      (45 lines — project-wide essentials)
src/backend/AGENTS.md          (64 lines — Python, Django, DB, API, logging, security)
src/frontend/AGENTS.md         (25 lines — React, TypeScript, accessibility)
```

### What moved where

| Content | From | To |
|---------|------|----|
| Python Style (12 rules) | root | src/backend/AGENTS.md |
| Django Conventions (9 rules) | root | src/backend/AGENTS.md |
| Database (5 rules) | root | src/backend/AGENTS.md |
| API Design (7 rules) | root | src/backend/AGENTS.md |
| Logging (6 rules) | root | src/backend/AGENTS.md |
| Security (5 of 6 rules) | root | src/backend/AGENTS.md |
| React Frontend (10 rules) | root | src/frontend/AGENTS.md |
| Backend test details (factory_boy, Django test client) | root Testing | src/backend/AGENTS.md |
| Frontend test details (Jest, RTL) | root Testing | src/frontend/AGENTS.md |

### What stayed in root
- Project description (1 line)
- Build/test/lint commands (universal `make` commands + per-stack install)
- Git workflow
- CI/CD pipeline
- Cross-cutting testing standards (coverage threshold, mocking, parameterization, E2E)
- Environment & security essentials (env vars, secrets, HTTPS, dependabot)
- Links to subdirectory AGENTS files

### Deletion candidates
| Item | Reason |
|------|--------|
| Root "Package Managers" section | Redundant — the build commands already show `pip` and `npm`; subdirectory files now specify install commands |
| Root "Python Style" section | Moved entirely to backend (domain-specific) |
| Root "Django Conventions" section | Moved entirely to backend |
| Root "React Frontend" section | Moved entirely to frontend |
| Root "API Design" section | Moved entirely to backend |
| Root "Logging" section | Backend-specific (structlog, request_id) |
| Root security items "bandit", "parameterized queries", "CSRF/CORS", "validate input" | Backend-specific; kept "dependabot" and "HTTPS" in root |

## D. Combined Preview

### `AGENTS.md` (45 lines)

```markdown
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
```

### `src/backend/AGENTS.md` (64 lines)

```markdown
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
```

### `src/frontend/AGENTS.md` (25 lines)

```markdown
# Frontend Instructions

React frontend with TypeScript.

## Build & Test

- Install: `npm install`
- Build: `npm run build`
- Tests: `npm test` (Jest + React Testing Library)
- Lint: `npm run lint`

## Conventions

- Components in frontend/src/components/
- TypeScript strict mode
- React Query for API calls
- Zustand for state management
- CSS Modules for styling
- Use data-testid for test selectors
- Lazy load route-level components
- Use rem units, not px

## Accessibility

- All forms need accessible labels and error messages
```

## Summary

| File | Before | After | Change |
|------|--------|-------|--------|
| `AGENTS.md` | 125 lines | 45 lines | −64% |
| `src/backend/AGENTS.md` | 25 lines | 64 lines | +156% (absorbed root content) |
| `src/frontend/AGENTS.md` | 21 lines | 25 lines | +19% (minor enrichment) |
| **Total** | **171 lines** | **134 lines** | **−22%** (removed duplication) |

**Zero information lost.** Every rule from the original files is preserved in exactly one location. Root now contains only project-wide essentials and links to domain-specific files.
