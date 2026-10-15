STACK DETECTED
- Repo: `evals/files/react-router-fixture/`
- Dependencies from `package.json`:
  - `react-router-dom`: `7.6.2`
  - `react`: `^19.0.0`
- Target file `src/nav.ts` currently uses `useHistory` + `history.push`.

OFFICIAL SOURCES
- React Router v7.6.2 `useNavigate` API: https://reactrouter.com/7.6.2/api/hooks/useNavigate
- React Router v7.6.2 declarative navigation guide: https://reactrouter.com/7.6.2/start/declarative/navigating
- React Router v7.6.2 docs home/versioned nav (version context): https://reactrouter.com/7.6.2/home

IMPLEMENTATION NOTES
- For React Router `7.6.2`, official docs describe programmatic navigation via `useNavigate`, not `useHistory`.
- Documented pattern is: get `navigate` from `useNavigate()` and call `navigate("/checkout")` (or `navigate("/checkout", { replace: true })` if replace semantics required).
- This request asked for no code changes, so guidance only: `src/nav.ts` should be migrated from history API usage to `useNavigate` pattern per v7.6.2 docs.

UNVERIFIED
- Import path conventions in cited v7.6.2 docs show examples from `"react-router"`; this fixture depends on `"react-router-dom"`. The provided fixture context does not include additional project conventions to resolve whether import paths should be standardized now, so only the hook/API migration (`useHistory` → `useNavigate`) is fully verified here.
