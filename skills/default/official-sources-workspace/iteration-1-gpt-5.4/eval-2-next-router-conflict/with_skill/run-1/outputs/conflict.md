# STACK DETECTED

- Fixture dependency: `next` **15.3.1** (`evals/files/next-conflict-fixture/package.json`)
- Current helper: `src/use-dashboard-router.ts` imports `useRouter` from `next/router`

# OFFICIAL SOURCES

1. App Router `useRouter` docs: https://nextjs.org/docs/app/api-reference/functions/use-router  
   - Current official guidance: import `useRouter` from `next/navigation`, not `next/router`, when using App Router.
   - Example also shows App Router usage inside a Client Component.
2. Pages Router `useRouter` docs: https://nextjs.org/docs/pages/api-reference/functions/use-router  
   - Official Pages Router API still uses `import { useRouter } from 'next/router'`.
3. App Router migration guide: https://nextjs.org/docs/app/guides/migrating/app-router-migration  
   - Official guide says `app` and `pages` can coexist during migration.
4. `next/compat/router` docs: https://nextjs.org/docs/pages/api-reference/functions/use-router#the-nextcompatrouter-export  
   - Official bridge for components that must work in both `app` and `pages`.

# CONFLICT

Current docs do **not** support one silent answer here:

- If `use-dashboard-router.ts` is meant for **Pages Router**, existing `next/router` import is still officially correct.
- If it is meant for **App Router**, official docs say this should move to `next/navigation` instead, and App Router examples assume Client Component usage.

This fixture provides only `src/use-dashboard-router.ts` plus `package.json`; it does **not** show whether this hook is consumed from `pages/`, `app/`, or both. Because Next.js **15.3.1** supports both router systems, choosing `next/router` vs `next/navigation` from version alone would be guesswork.

# IMPLEMENTATION NOTES

Do **not** change code yet without deciding intended router mode:

- **Choose Pages Router path** if this helper is only used from `pages/*` components. Then `next/router` remains aligned with official docs.
- **Choose App Router path** if this helper is for `app/*` Client Components. Then align with official docs by using `next/navigation` instead of `next/router`.
- **Choose migration/dual-support path** only if this helper must work across both systems. Official docs point to `next/compat/router` as transition aid, with App Router hooks from `next/navigation` where needed.

Result: **documented doc/codebase conflict surfaced; no code change selected yet.**
