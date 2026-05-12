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

## Environment

- `.env` for local config — never commit `.env` files
- Required: `DATABASE_URL`, `JWT_SECRET`, `REDIS_URL`, `BASE_URL` (API client base URL)
- Optional: `LOG_LEVEL` (default: info), `PORT` (default: 3000)

## Git Workflow

- Branch from main; PR required for all changes
- Squash merge only
- Commit format: `type(scope): description`
- Run lint and tests before pushing

## Scoped Guides

- [`src/api/AGENTS.md`](src/api/AGENTS.md) — backend, API, and database conventions
- [`src/components/AGENTS.md`](src/components/AGENTS.md) — frontend and React conventions
