STACK DETECTED:
- Next.js (15.3.1)
- React (^19.0.0)

OFFICIAL SOURCES:
- https://nextjs.org/docs/app/api-reference/functions/use-router

IMPLEMENTATION NOTES:
- Codebase conflict detected.
- Existing code `src/use-dashboard-router.ts` imports `useRouter` from `next/router` (Pages Router).
- Official docs for Next.js 15 state `useRouter` should be imported from `next/navigation` for App Router.
- Need guidance: Follow documented current pattern (`next/navigation`) or existing codebase pattern (`next/router`)?

UNVERIFIED:
- none
