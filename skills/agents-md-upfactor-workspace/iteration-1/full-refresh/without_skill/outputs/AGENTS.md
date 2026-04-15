# Project Guide

Full-stack TypeScript application — React frontend, Express backend.

## Build & Test

- Package manager: **npm** (lock file: `package-lock.json`)
- `npm run build` — builds frontend and backend
- `npm test` — runs all tests (unit + integration + e2e)
- `npm run test:unit` — unit tests only; **prefer this for fast iteration**
- `npm run lint` — ESLint (note: ignores `src/generated/`)

## Code Style

- TypeScript strict mode everywhere
- Prefer named exports over default exports
- `interface` for object shapes, `type` for unions/intersections
- Prefer `const` over `let`; never use `var`
- Arrow functions for callbacks
- `async/await` over `.then()` chains

## Frontend

### Structure

- Components: `src/components/`
- Pages: `src/pages/`
- Shared hooks: `src/hooks/`

### Conventions

- All React components must be functional components with hooks
- Use React Query for server state, Zustand for client state
- Use CSS modules for styling (not inline styles); follow BEM naming for class names
- Use `rem` units for spacing, not `px`
- Keep component files under 200 lines; extract sub-components when longer
- Use Suspense boundaries around lazy-loaded routes
- Memoize expensive computations with `useMemo`
- Prefix event handlers with "handle" (e.g., `handleSubmit`)
- All forms must have accessible labels

### Testing

- Use React Testing Library
- Prefer `data-testid` attributes for test selectors

## Backend

### Structure

- Routes: `src/api/routes/`
- Controllers: `src/api/controllers/`
- Services: `src/api/services/`
- Models: `src/api/models/`

### API Conventions

- Use Express Router for route grouping
- Return consistent JSON: `{ data, error, meta }`
- Validate request bodies with zod schemas
- Use middleware for auth checks, not inline code
- Log all 5xx errors with full stack trace
- Rate limit all public endpoints
- Use parameterized queries — never string interpolation for SQL

### API Client (`src/api/`)

- Requires the `BASE_URL` environment variable (e.g., `https://api.example.com`)
- All outgoing HTTP requests use `BASE_URL` as the root URL

### Testing

- Write unit tests for all service methods
- Use dependency injection for services
- Integration tests go in `__tests__/integration/`
- Mock external APIs in tests — never hit real endpoints
- Use transactions for multi-step DB operations

## Database

- PostgreSQL via Prisma ORM
- Migrations: `prisma/migrations/` — create with `npx prisma migrate dev`
- Seed data: `prisma/seed.ts`
- Never modify migration files after they've been applied

## Environment

- `.env` for local config — never commit `.env` files
- Required: `DATABASE_URL`, `JWT_SECRET`, `REDIS_URL`, `BASE_URL` (API client base URL)
- Optional: `LOG_LEVEL` (default: info), `PORT` (default: 3000)

## Git Workflow

- Branch from main; PR required for all changes
- Squash merge only
- Commit format: `type(scope): description`
- Run lint and tests before pushing
