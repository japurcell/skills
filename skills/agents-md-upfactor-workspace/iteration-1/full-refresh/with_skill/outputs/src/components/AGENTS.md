# Frontend Conventions

## Components

- Components in `src/components/`; pages in `src/pages/`
- All React components must be functional with hooks
- Keep files under 200 lines; extract sub-components if longer
- Event handlers prefixed with "handle" (e.g., `handleSubmit`)

## Styling

- Use CSS modules, not inline styles
- Use `rem` units for spacing, not `px`
- Follow BEM naming for CSS class names

## State & Data

- React Query for server state; Zustand for client state
- Shared hooks in `src/hooks/`
- Memoize expensive computations with `useMemo`

## Routing

- Use Suspense boundaries around lazy-loaded routes

## Testing

- Test with React Testing Library
- Use `data-testid` attributes for test selectors

## Accessibility

- All forms must have accessible labels
