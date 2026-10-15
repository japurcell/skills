# React Router Programmatic Navigation Guidance

## STACK DETECTED
- React: ^19.0.0
- React Router: 7.6.2 (from `react-router-dom` in `package.json`)

## OFFICIAL SOURCES
- [useNavigate hook - React Router](https://reactrouter.com/api/hooks/useNavigate)

## IMPLEMENTATION NOTES
- Programmatic navigation in React Router 7 is handled by the `useNavigate` hook.
- Import `useNavigate` from `"react-router"`.
- Call `useNavigate()` inside a component to obtain the `navigate` function.
- The `navigate` function signature is `navigate(to, options?)` or `navigate(delta)`:
  - `to` can be a string path (e.g., `"/some/route"`), a `To` object (e.g., `{ pathname: "/some/route", search: "?search=param" }`), or a number to traverse the history stack (e.g., `navigate(-1)` to go back).
  - `options` can include `replace: true` (to replace the current history entry), `state: { ... }` (to pass state to the new location), and `preventScrollReset: true` (to prevent scrolling to the top).
- It is often better to use `redirect` in `action` or `loader` functions rather than `useNavigate` if programmatic navigation is needed as part of data fetching/mutations.
- Example:
  ```tsx
  import { useNavigate } from "react-router";

  export function SomeComponent() {
    let navigate = useNavigate();
    
    return (
      <button onClick={() => navigate("/next-page", { replace: true })}>
        Go to Next Page
      </button>
    );
  }
  ```

## UNVERIFIED
- None.
