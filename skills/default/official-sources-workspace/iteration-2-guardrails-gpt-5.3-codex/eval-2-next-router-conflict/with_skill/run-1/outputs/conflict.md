STACK DETECTED
- Repo: `evals/files/next-conflict-fixture/`
- `next`: `15.3.1` (from `package.json`)
- `react`: `^19.0.0`
- Current file `src/use-dashboard-router.ts` imports `useRouter` from `next/router`.

OFFICIAL SOURCES
- Next.js v15 App Router `useRouter` (import from `next/navigation`): https://nextjs.org/docs/15/app/api-reference/functions/use-router
- Next.js v15 Pages Router `useRouter` (import from `next/router`): https://nextjs.org/docs/15/pages/api-reference/functions/use-router
- Next.js v15 App Router migration guide (explicit migration from `next/router`): https://nextjs.org/docs/15/app/guides/migrating/app-router-migration

CONFLICT
- Official docs support **two valid patterns**, tied to router architecture:
  1. **App Router code**: `useRouter` from `next/navigation`
  2. **Pages Router code**: `useRouter` from `next/router`
- Existing code uses Pages Router import (`next/router`).
- But task asks for “current Next.js docs” and fixture does not provide enough routing-context evidence (`app/` vs `pages/` usage) to choose one safely.

OPTIONS (do not apply yet)
- If this helper is for **App Router** components, migrate import/API usage to `next/navigation` and follow App Router semantics.
- If this helper is for **Pages Router** components, keep `next/router`; current code already matches official v15 Pages docs.

UNVERIFIED
- Router mode for this codepath (App vs Pages) cannot be verified from provided fixture files alone, so selecting one path now would be guesswork.
