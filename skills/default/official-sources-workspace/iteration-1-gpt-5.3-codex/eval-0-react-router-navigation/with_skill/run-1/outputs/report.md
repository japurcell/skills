STACK DETECTED
- Fixture: `evals/files/react-router-fixture/`
- `react-router-dom`: `7.6.2` (from `package.json`)
- `react`: `^19.0.0` (from `package.json`)
- Target file: `src/nav.ts` currently uses `useHistory()` + `history.push("/checkout")`.

OFFICIAL SOURCES
- React Router API: `useNavigate` (programmatic navigation): https://reactrouter.com/api/hooks/useNavigate
- React Router guide (Framework/Data): navigating guidance and when to prefer `redirect`/links: https://reactrouter.com/start/framework/navigating
- React Router guide (Declarative): `Link`/`NavLink` preferred, `useNavigate` for non-interactive flows: https://reactrouter.com/start/declarative/navigating
- React Router API: `redirect` utility (recommended in loaders/actions): https://reactrouter.com/api/utils/redirect
- React Router API route for `useHistory` returns 404 in current docs: https://reactrouter.com/api/hooks/useHistory

IMPLEMENTATION NOTES
- Current official programmatic navigation hook is `useNavigate`, with `navigate("/checkout")`.
- Official docs explicitly recommend using `Link`/`NavLink` for normal user-initiated navigation.
- Official docs also say it is often better to use `redirect(...)` in loader/action flows than `useNavigate`.
- For `src/nav.ts` intent (imperative navigation helper), current documented pattern aligns with `useNavigate` + returned callback that calls `navigate("/checkout")`.
- `useHistory` is not documented in current React Router docs; current API index lists `useNavigate` instead.

UNVERIFIED
- Could not confirm from fetched official pages whether this fixture is using Declarative mode vs Data/Framework mode; guidance above uses docs that are consistent across those modes for `useNavigate` usage.
- Did not verify from fetched docs whether this project should import hook from `react-router` vs `react-router-dom` in this exact setup; docs examples show `react-router` on current site.
