## STACK DETECTED
- Fixture path: `evals/files/react-router-fixture/`
- React: `^19.0.0` (from `package.json`)
- React Router DOM: `7.6.2` (from `package.json`)
- Target file: `src/nav.ts` currently uses `useHistory().push(...)`.

## OFFICIAL SOURCES
- React Router `useNavigate` API (official): https://reactrouter.com/api/hooks/useNavigate
- React Router declarative navigation guide (official): https://reactrouter.com/start/declarative/navigating
- React Router upgrade guidance noting `useNavigate()` for navigation (official): https://reactrouter.com/6.30.1/upgrading/v5

## IMPLEMENTATION NOTES
- Current official programmatic navigation hook is `useNavigate` (returns `navigate(to, options?)` / `navigate(delta)`).
- Official guidance says use `Link`/`NavLink` for normal user-click navigation; reserve `useNavigate` for non-interactive/programmatic flows.
- For `src/nav.ts` checkout navigation intent, current documented pattern is a navigate function call like `navigate("/checkout")`.
- Existing file uses legacy `useHistory().push("/checkout")`, which conflicts with current documented guidance.

## UNVERIFIED
- none
