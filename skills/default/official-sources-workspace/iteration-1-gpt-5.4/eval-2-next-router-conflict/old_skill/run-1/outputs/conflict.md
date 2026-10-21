STACK DETECTED
- Next.js 15.3.1 from package.json
- React ^19.0.0 from package.json

OFFICIAL SOURCES
- App Router useRouter: https://nextjs.org/docs/15/app/api-reference/functions/use-router
- Pages Router useRouter: https://nextjs.org/docs/15/pages/api-reference/functions/use-router
- App Router migration guide: https://nextjs.org/docs/15/app/guides/migrating/app-router-migration

CONFLICT
- Existing code in src/use-dashboard-router.ts imports useRouter from next/router, which matches Next.js Pages Router docs.
- Current official App Router docs say: "The useRouter hook should be imported from next/navigation and not next/router when using the App Router".
- Next.js 15 docs also say pages and app can coexist during migration, so correct import depends on which router this helper is meant to serve.
- Fixture repo does not include app/ or pages/ directories, so router mode is not verifiable from codebase as given.

WHAT THIS MEANS FOR src/use-dashboard-router.ts
- If helper is for Pages Router, current code pattern is still documented: import { useRouter } from next/router.
- If helper is for App Router or migration target, current docs require switching to import { useRouter } from next/navigation.

RECOMMENDED NEXT DECISION
- Choose one explicitly before changing code:
  1. Keep Pages Router pattern (next/router) because helper serves pages routes.
  2. Migrate helper to App Router pattern (next/navigation) because helper serves app routes.

UNVERIFIED
- Exact patch-level docs for 15.3.1 were not available; official Next 15 docs currently resolve to 15.5.19, which is closest official version stream.
