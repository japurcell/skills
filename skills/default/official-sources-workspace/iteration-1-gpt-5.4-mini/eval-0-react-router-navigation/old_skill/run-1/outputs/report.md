STACK DETECTED
- React 19.0.0
- react-router-dom 7.6.2
- Target file: src/nav.ts
- Current pattern: `useHistory().push("/checkout")`

OFFICIAL SOURCES
- https://reactrouter.com/api/hooks/useNavigate
  - `useNavigate` returns a function for programmatic navigation.
  - Signature: `navigate(to, options?)` / `navigate(delta)`.
  - Docs show `navigate("/some/route")` and `navigate("/some/route", { replace: true })`.
- https://reactrouter.com/start/framework/navigating
  - `useNavigate` is listed as one of the navigation APIs.
  - Docs say usage should be uncommon and best reserved for non-interactive navigation.

IMPLEMENTATION NOTES
- Current code should use `useNavigate` instead of `useHistory`.
- `history.push("/checkout")` maps to `navigate("/checkout")`.
- If this flow should replace the current entry, use `navigate("/checkout", { replace: true })`.
- React Router v7 docs examples import from `react-router`.

UNVERIFIED
- I did not verify whether this fixture's build setup requires the import path to stay `react-router-dom` instead of `react-router`.
- I did not verify any app-specific reason to prefer `replace: true` over push behavior.
