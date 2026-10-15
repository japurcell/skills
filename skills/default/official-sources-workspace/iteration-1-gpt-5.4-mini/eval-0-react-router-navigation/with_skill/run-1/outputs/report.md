# STACK DETECTED
- React 19.0.0
- react-router-dom 7.6.2
- Target file: `src/nav.ts`
- Current code uses `useHistory` from `react-router-dom`

# OFFICIAL SOURCES
- React Router v7.6.2 `useNavigate`: https://reactrouter.com/7.6.2/api/hooks/useNavigate
- React Router v7.6.2 Navigating guide: https://reactrouter.com/7.6.2/start/framework/navigating
- React Router v7.6.2 upgrade guide: https://reactrouter.com/7.6.2/upgrading/v6

# IMPLEMENTATION NOTES
- Current guidance for programmatic navigation is `useNavigate`, not `useHistory`.
- Docs show `useNavigate()` returns a navigation function and is meant for user-driven effects or uncommon programmatic redirects.
- For this repo/version, import hooks from `react-router` in v7 docs examples.
- The code in `src/nav.ts` should be updated conceptually to:
  - replace `useHistory()` with `useNavigate()`
  - replace `history.push("/checkout")` with `navigate("/checkout")`

# UNVERIFIED
- I did not verify whether this fixture uses `BrowserRouter`, `RouterProvider`, or framework/data mode, so return type details (`void` vs `Promise<void>`) are unverified for this app.
- I did not change code, only reviewed official guidance.
