STACK DETECTED
- Next.js 15.3.1
- React 19.0.0
- `src/use-dashboard-router.ts` imports `useRouter` from `next/router`.

OFFICIAL SOURCES
- Next.js App Router `useRouter`: https://nextjs.org/docs/app/api-reference/functions/use-router
- Next.js Pages Router `useRouter`: https://nextjs.org/docs/pages/api-reference/functions/use-router

CONFLICT
- Existing code matches the Pages Router API: official Pages Router docs document `useRouter` from `next/router`.
- Current App Router docs say `useRouter` should be imported from `next/navigation`, not `next/router`, when using the App Router.
- Repo fixture does not include enough routing structure (`app/` vs `pages/`) to determine which router architecture this project uses.
- Because current official docs support different imports based on router mode, I cannot recommend keeping `next/router` or switching to `next/navigation` without first resolving whether this app is Pages Router or App Router.

NEEDS DECISION
- If this code belongs to a Pages Router app, current helper is aligned with official docs.
- If this code belongs to an App Router client component, official docs indicate it should use `next/navigation` instead.

UNVERIFIED
- Router mode is not identifiable from the provided project files alone.
