STACK DETECTED
- React 19.0.0
- react-router-dom 7.6.2
- `src/nav.ts` uses `useHistory()` plus `history.push("/checkout")`.

OFFICIAL SOURCES
- React Router `useNavigate`: https://reactrouter.com/api/hooks/useNavigate
- React Router declarative navigation guide: https://reactrouter.com/start/declarative/navigating
- React Router declarative installation guide: https://reactrouter.com/start/declarative/installation

IMPLEMENTATION NOTES
- Current official programmatic-navigation hook is `useNavigate`, which returns a navigate function and documents `navigate("/some/route")` for path changes.
- Current declarative-mode docs say normal user-triggered navigation should prefer `<Link>` or `<NavLink>` and reserve `useNavigate` for programmatic flows such as post-submit redirects or time-based redirects.
- `useHistory` does not appear in the current official hook reference; this file is using an older pattern relative to the current docs.
- Current official declarative docs show imports from `react-router`, not `react-router-dom`.

UNVERIFIED
- I did not verify a React Router 7.6.2 patch-specific doc page. The fetched official docs are current React Router docs, so exact package-import guidance for this repo's pinned `react-router-dom@7.6.2` remains unverified.
