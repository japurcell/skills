STACK DETECTED: next 15.3.1
OFFICIAL SOURCES:
- https://nextjs.org/docs/app/api-reference/functions/use-router
- https://nextjs.org/docs/pages/api-reference/functions/use-router

ROUTER-CONTEXT CHOICE: App Router. Use `next/navigation`, not `next/router`.

IMPLEMENTATION NOTES:
- `next/navigation` is the App Router hook for Client Components.
- `next/router` is the Pages Router hook.
- Current file imports `useRouter` from `next/router`, which conflicts with Next 15 App Router usage.
- Change import to `next/navigation` before any behavior code.
