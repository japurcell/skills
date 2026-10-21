STACK DETECTED
Next.js v15.3.1 (from `package.json`)

OFFICIAL SOURCES
- [Next.js App Router API Reference for `useRouter`](https://nextjs.org/docs/app/api-reference/functions/use-router)
- [Next.js Pages Router API Reference for `useRouter`](https://nextjs.org/docs/pages/api-reference/functions/use-router)

IMPLEMENTATION NOTES
The official Next.js documentation highlights a difference between routing APIs depending on the architecture in use:
- **App Router:** `useRouter` should be imported from `next/navigation`.
- **Pages Router:** `useRouter` is imported from `next/router`.

The existing code in `src/use-dashboard-router.ts` relies on the Pages Router API:
```typescript
import { useRouter } from "next/router";
```

**Conflict:** The current App Router documentation recommends `next/navigation` for `useRouter`, but the codebase is using `next/router`. Before updating the code, please confirm whether this project is migrating to the App Router (requiring `next/navigation` and other hook changes like `usePathname`), or if it should remain on the Pages Router.