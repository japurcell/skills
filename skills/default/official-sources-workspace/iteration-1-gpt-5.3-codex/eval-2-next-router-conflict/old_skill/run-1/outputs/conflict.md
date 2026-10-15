STACK DETECTED
- next: 15.3.1 (from `evals/files/next-conflict-fixture/package.json`)
- react: ^19.0.0

OFFICIAL SOURCES
- Next.js 15 App Router `useRouter`: https://nextjs.org/docs/15/app/api-reference/functions/use-router
  - Says App Router should import `useRouter` from `next/navigation` ("The `useRouter` hook should be imported from `next/navigation` and not `next/router` when using the App Router").
- Next.js 15 Pages Router `useRouter`: https://nextjs.org/docs/15/pages/api-reference/functions/use-router
  - Documents `useRouter` import from `next/router` for Pages Router.

CONFLICT
- Current code (`src/use-dashboard-router.ts`) imports `useRouter` from `next/router`.
- File is under `src/` with no explicit `pages/` or `app/` context in fixture, so router mode is ambiguous.
- Official docs support both imports, but for different router systems:
  - App Router pattern: `next/navigation`
  - Pages Router pattern: `next/router`
- Because repo context does not prove which router system this helper targets, changing import now would be a silent assumption.

IMPLEMENTATION DECISION (DEFERRED)
- Do not change code yet.
- Resolve first: is this helper for App Router or Pages Router?
  - If App Router: migrate to `next/navigation` per Next.js 15 App Router docs.
  - If Pages Router: keep `next/router` per Next.js 15 Pages Router docs.
