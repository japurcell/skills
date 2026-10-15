STACK DETECTED

- Inspected `package.json` and `src/nav.ts`.
- React: declared dependency `^19.0.0` (exact resolved install version not present in inspected files).
- React Router DOM: `7.6.2`.
- `src/nav.ts` currently uses `useHistory()` and `history.push("/checkout")`.
- Router mode is likely declarative/client-side routing, but router setup is not present in inspected files.

OFFICIAL SOURCES

- React Router 7.6.2 Declarative Navigating: https://reactrouter.com/7.6.2/start/declarative/navigating  
  Says declarative apps navigate with `<Link>`, `<NavLink>`, and `useNavigate`, and recommends `Link`/`NavLink` for normal navigation while reserving `useNavigate` for programmatic flows.
- React Router 7.6.2 `useNavigate` API: https://reactrouter.com/7.6.2/api/hooks/useNavigate  
  Documents programmatic navigation as `navigate(to, options?)` / `navigate(delta)`, including `replace` and `state` options.
- React Router 7.6.2 Declarative Installation: https://reactrouter.com/7.6.2/start/declarative/installation  
  Current v7 declarative docs show router APIs imported from `react-router`.

IMPLEMENTATION NOTES

- Current official React Router 7.6.2 guidance for programmatic navigation is `useNavigate`, not `useHistory`.
- Documented equivalent to `history.push("/checkout")` is `navigate("/checkout")`.
- If this navigation is triggered by ordinary user interaction whose main purpose is changing pages, official docs prefer `<Link>` or `<NavLink>` over imperative navigation.
- If imperative navigation is still desired in a hook/callback, current 7.6.2 declarative docs show `useNavigate` imported from `react-router`.
- If replace semantics are needed, official API is `navigate("/checkout", { replace: true })`; if location state is needed, pass `state` in the options object.

UNVERIFIED

- Exact installed React version cannot be confirmed from inspected files; only declared range `^19.0.0` is visible.
- Router mode is inferred, not proven, because no router setup file was included in the fixture.
- Whether this repo intentionally depends on `react-router-dom` re-exports instead of current `react-router` imports cannot be confirmed from inspected files alone.
