STACK DETECTED
- Next.js 15.3.1
- react ^19.0.0

OFFICIAL SOURCES
- App Router `useRouter`: https://nextjs.org/docs/app/api-reference/functions/use-router
  - Docs show `useRouter` imported from `next/navigation`.
  - Migration note: import from `next/navigation`, not `next/router`, when using the App Router.
- Pages Router `useRouter`: https://nextjs.org/docs/pages/api-reference/functions/use-router
  - Docs keep `useRouter` from `next/router` for Pages Router.

CONFLICT
- `src/use-dashboard-router.ts` imports `useRouter` from `next/router`.
- Current App Router docs for Next.js recommend `next/navigation` instead.
- If this fixture is App Router code, helper should change.
- If this fixture is Pages Router code, existing import is correct.
- Need repo/router-context confirmation before editing.

UNVERIFIED
- App Router vs Pages Router structure is not visible in fixture.
