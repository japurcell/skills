# AGENTS.md Reorganization

## What Changed

Reorganized 3 AGENTS.md files to eliminate duplication and establish clear ownership:

### Root `AGENTS.md` (126 → 62 lines)
- **Removed**: Python style, Django conventions, database rules, React frontend rules, API design — all moved to domain-specific files
- **Kept**: Project overview, top-level build commands, package managers, testing strategy (cross-cutting), environment, CI/CD, git workflow, logging, security
- **Added**: Links to subdirectory AGENTS.md files for discoverability

### `src/backend/AGENTS.md` (26 → 53 lines)
- **Added from root**: Full Python style guide (Pydantic, isort, pathlib, f-strings, context managers, bare except rule), complete Django conventions (apps location, signals, management commands), database rules (PostgreSQL, migrations), API design (endpoints, auth, rate limiting, OpenAPI)
- **Kept**: Build commands, core Django and Python rules
- Now the single source of truth for all backend concerns

### `src/frontend/AGENTS.md` (22 → 32 lines)
- **Restructured** into logical sections: Build & Test, Component Structure, TypeScript & React Conventions, Testing, Accessibility
- **Added from root**: Error messages requirement for forms, component directory location
- Now the single source of truth for all frontend concerns

## Principle
Each file owns its domain. The root handles cross-cutting project concerns; subdirectory files handle domain-specific rules. No content is duplicated across files.
