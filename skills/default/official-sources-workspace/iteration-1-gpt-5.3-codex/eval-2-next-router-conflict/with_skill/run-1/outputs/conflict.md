# Conflict: `src/use-dashboard-router.ts` routing helper (no code changes)

## STACK DETECTED
- `next` version in fixture: **15.3.1** (`evals/files/next-conflict-fixture/package.json`)
- Relevant official docs snapshot for major 15 are versioned under `/docs/15/*` (currently shows `15.5.19` on those pages).

## OFFICIAL SOURCES
1. App Router `useRouter` (Next 15): import from **`next/navigation`**, and migration notes explicitly say not to use `next/router` in App Router.  
   https://nextjs.org/docs/15/app/api-reference/functions/use-router
2. Pages Router `useRouter` (Next 15): import from **`next/router`**.  
   https://nextjs.org/docs/15/pages/api-reference/functions/use-router
3. App Router migration guide, Step 5: `next/router` hook is **not supported in `app` directory**; use `next/navigation` hooks, or `next/compat/router` for shared transitional components.  
   https://nextjs.org/docs/15/app/guides/migrating/app-router-migration#step-5-migrating-routing-hooks
4. Error reference: using `next/router` in `app` can trigger `NextRouter` not mounted guidance to migrate to `next/navigation`.  
   https://nextjs.org/docs/messages/next-router-not-mounted

## CODEBASE OBSERVED
- `src/use-dashboard-router.ts` currently does:
  - `import { useRouter } from "next/router";`
  - returns `useRouter()` directly.

## CONFLICT
- Official docs define **two valid-but-context-specific patterns**:
  - `next/navigation` for **App Router**
  - `next/router` for **Pages Router**
- Existing code picks `next/router`, but fixture context does not prove whether this helper is used from `app` routes, `pages` routes, or shared code.
- Therefore, updating now without broader routing context would risk choosing wrong documented pattern.

## DECISION (PER REQUEST: NO CODE CHANGE YET)
Conflict surfaced, not resolved in code.  
Required follow-up before implementation: determine helper runtime context (`app`, `pages`, or shared) and then apply matching official pattern.
