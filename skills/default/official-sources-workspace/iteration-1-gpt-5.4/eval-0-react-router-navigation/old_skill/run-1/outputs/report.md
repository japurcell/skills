# STACK DETECTED
- React app fixture with TypeScript source (`src/nav.ts`).
- `package.json` declares `react` `^19.0.0` and `react-router-dom` `7.6.2`.
- `src/nav.ts` currently imports `useHistory` from `react-router-dom` and calls `history.push("/checkout")`.

# OFFICIAL SOURCES
- https://reactrouter.com/7.6.2/api/hooks/useNavigate — official v7.6.2 API for programmatic navigation; documents `useNavigate()` and `navigate("/some/route")`.
- https://reactrouter.com/7.6.2/start/declarative/navigating — official declarative-mode guide; says users navigate with `<Link>`, `<NavLink>`, and `useNavigate`, and to reserve `useNavigate` for imperative cases.
- https://reactrouter.com/7.6.2/start/declarative/installation — official v7.6.2 setup guide; shows `<BrowserRouter>` imported from `react-router`.
- https://reactrouter.com/7.6.2/upgrading/v6 — official v7 upgrade guide; says v7 no longer needs `react-router-dom` and imports should be updated to `react-router`.
- https://reactrouter.com/7.6.2/api/hooks/useHistory — official 7.6.2 docs page resolves to 404, which is consistent with `useHistory` not being a documented v7 hook.

# IMPLEMENTATION NOTES
- Current React Router 7.6.2 guidance for programmatic navigation is `useNavigate()`, then call `navigate("/checkout")`.
- `useHistory().push(...)` is not the documented v7.6.2 programmatic-navigation API.
- Official v7 docs prefer imports from `react-router` for declarative routing APIs. If `src/nav.ts` is updated later to match docs, documented shape is `import { useNavigate } from "react-router"; const navigate = useNavigate(); return () => navigate("/checkout");`.
- Official docs also say `Link`/`NavLink` are preferred for normal user-driven navigation; keep imperative navigation only if this hook is needed outside normal link interactions.

# UNVERIFIED
- Whether this repo intentionally relies on `react-router-dom` re-exports in v7; fetched official 7.6.2 docs here verify `react-router` imports, not a `react-router-dom`-specific recommendation for this hook.
- Router mode/bootstrap file is not present in fixture, so `BrowserRouter` usage in this specific repo cannot be confirmed from project files alone.
