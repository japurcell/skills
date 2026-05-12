# AGENTS.md Refresh — Summary

## What Changed

### Session learnings captured

1. **`npm run test:unit` added** — Documented as the preferred fast-iteration test command, with `npm test` noted as the slower full-suite option for final validation.

2. **`BASE_URL` env var documented** — Added to both the Environment section (as a required var) and a new "API Client" subsection under Backend, explaining that `src/api/` depends on it for outgoing HTTP requests.

3. **ESLint ignores `generated/`** — Added a note to the Build & Test section that ESLint skips `src/generated/`.

### Structural cleanup

4. **Separated frontend and backend into top-level sections** — The old file had a flat "Code Style" section mixing React-specific rules (CSS modules, BEM, `useMemo`, component size limits) with shared TypeScript rules. Now:
   - **Code Style** contains only shared TypeScript conventions
   - **Frontend** has its own Structure, Conventions, and Testing subsections
   - **Backend** has its own Structure, API Conventions, API Client, and Testing subsections

5. **Tightened prose** — Removed redundant wording, consolidated related bullet points (e.g., CSS modules + BEM naming merged into one line), and made the intro more concise.

6. **Merged Package Manager into Build & Test** — Eliminated a two-line section; package manager is now a single line at the top of Build & Test.

### No information lost

Every rule from the original AGENTS.md is preserved in the updated version — just reorganized into clearer sections.
