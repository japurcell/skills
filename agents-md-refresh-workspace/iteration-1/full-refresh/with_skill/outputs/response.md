# AGENTS.md Refresh — Session Results

## A. Contradictions

None found. All existing rules are consistent.

---

## B. New Learnings (from session)

Three discoveries captured and integrated:

### 1. Fast unit test command

**Target**: `./AGENTS.md` Build & Test + `src/api/AGENTS.md` Testing

```diff
+ - `npm run test:unit` — unit tests only; prefer this for fast iteration
```

### 2. Undocumented BASE_URL env var

**Target**: `./AGENTS.md` Environment + `src/api/AGENTS.md` Environment

```diff
- - Required vars: DATABASE_URL, JWT_SECRET, REDIS_URL
+ - Required: DATABASE_URL, JWT_SECRET, REDIS_URL, BASE_URL (API client base URL)
```

```diff
+ - BASE_URL env var is required by the API client — set it in .env
```

### 3. ESLint ignores generated/

**Target**: `./AGENTS.md` Build & Test

```diff
- - npm run lint — runs ESLint across the project
+ - npm run lint — ESLint (note: ignores src/generated/)
```

---

## C. Structural Changes

**Problem**: The original 87-line root AGENTS.md mixed frontend-specific rules (CSS modules, BEM, React Query, Zustand) with backend rules (Express routes, Prisma, dependency injection) in one flat file.

**Solution**: Split into three scoped files with clear ownership.

### New file structure

```
AGENTS.md                      (38 lines — universal essentials)
src/api/AGENTS.md              (36 lines — backend, API, database)
src/components/AGENTS.md       (33 lines — frontend, React, styling)
```

### What moved where

| Content | From (root section) | To (new location) |
|---------|--------------------|--------------------|
| API route conventions | API Conventions | src/api/AGENTS.md > API Routes |
| Express Router, zod, middleware | API Conventions | src/api/AGENTS.md > API Routes |
| Database/Prisma rules | Database | src/api/AGENTS.md > Database |
| Controller/service/model paths | Backend Conventions | src/api/AGENTS.md > Project Structure |
| Backend testing rules | Backend Conventions | src/api/AGENTS.md > Testing |
| React component rules | Code Style + Frontend | src/components/AGENTS.md > Components |
| CSS modules, BEM, rem units | Code Style + Frontend | src/components/AGENTS.md > Styling |
| React Query, Zustand, hooks | Frontend Conventions | src/components/AGENTS.md > State & Data |
| Suspense boundaries | Frontend Conventions | src/components/AGENTS.md > Routing |
| React Testing Library | Frontend Conventions | src/components/AGENTS.md > Testing |
| Form accessibility | Frontend Conventions | src/components/AGENTS.md > Accessibility |

### What stayed in root

- One-line project description
- Package manager
- Build/test/lint commands (with new learnings baked in)
- Universal TypeScript code style (applies everywhere)
- Environment variables (with new BASE_URL)
- Git workflow
- Links to scoped guides

### Deletion candidates

None — all existing rules are actionable and specific enough to keep.

---

## D. Summary

| File | Status | Lines | What it owns |
|------|--------|-------|--------------|
| AGENTS.md | Rewritten | 87 > 38 | Universal essentials + links |
| src/api/AGENTS.md | New | 36 | Backend, API, DB, backend testing |
| src/components/AGENTS.md | New | 33 | React, styling, state, frontend testing |

Key changes:
1. Root slimmed 56% — from 87 to 38 lines. Only universal rules remain.
2. 3 session learnings added — test:unit shortcut, BASE_URL env var, ESLint generated/ exclusion.
3. Zero rules lost — every original instruction preserved in exactly one location.
4. Scoped files auto-load — agents working in src/api/ or src/components/ get relevant context without loading the full set.
