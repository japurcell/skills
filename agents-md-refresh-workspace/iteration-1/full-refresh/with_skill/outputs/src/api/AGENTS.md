# Backend & API Conventions

## API Routes

- All routes in `src/api/routes/`; use Express Router for grouping
- Return consistent JSON: `{ data, error, meta }`
- Validate request body with zod schemas
- Use middleware for auth checks, not inline code
- Log all 5xx errors with full stack trace
- Rate limit all public endpoints

## Database

- PostgreSQL via Prisma ORM; migrations in `prisma/migrations/`
- Create migrations: `npx prisma migrate dev`; seed data in `prisma/seed.ts`
- Never modify applied migration files
- Use parameterized queries — never string-interpolate SQL
- Use transactions for multi-step DB operations

## Project Structure

- Controllers: `src/api/controllers/`
- Services: `src/api/services/`
- Models: `src/api/models/`
- Use dependency injection for services

## Testing

- Unit tests for all service methods
- Integration tests in `__tests__/integration/`
- Mock external APIs — never hit real endpoints in tests
- `npm run test:unit` is fastest for iterating on service tests

## Environment

- `BASE_URL` env var is required by the API client — set it in `.env`
