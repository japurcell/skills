# Handoff

## Goal
- Resume and finish fixing the sync failure: reproduce the error in scripts/sync.sh, identify the missing environment variable, and implement a clear fix (guard/default and updated docs/tests) so sync succeeds in CI and locally.

## Current Status
- Done: Investigation narrowed the failure to scripts/sync.sh; runs fail due to a missing environment variable that causes an early exit.
- In progress: Reproduction and logs collected; no code changes applied.
- Next up: Identify the exact env var name and the intended source (CI secret, .env, or upstream script), then add a targeted fix and a clear error message or sensible default.

## Decisions and Constraints
- Keep the change minimal and localized to scripts/sync.sh (and CI config if needed).
- Avoid large refactors; prefer an explicit check with a helpful error or a safe default.
- Do not commit secrets into the repo.

## Relevant Files
- `scripts/sync.sh` — where the failure occurs; inspect for variables referenced without defaults and add a guard or default.
- `.env.example` — check for documented env var names and intended defaults (if present).
- `.github/workflows/*` — CI jobs that run sync; verify environment provisioning and secrets.
- `README.md` or docs (deployment/ops) — any docs mentioning required environment variables.
- Any recent run logs (e.g., CI job logs or local sync output) — contain the failing line and error text.

## Open Questions or Blockers
- Which exact environment variable is missing? (not yet identified)
- Is the variable supposed to come from CI secrets, a local .env, or an earlier script step?

## Recommended Next Step
- Run with tracing: `bash -x scripts/sync.sh` in the failing environment (or replicate CI run) to see the failing line and the unset variable name. Search `scripts/sync.sh` for `${VAR}` patterns without defaults, then confirm where that VAR should be set in CI or docs. Implement a minimal guard (e.g., check and exit with a clear message or set a safe default) and update `.env.example` / CI workflow accordingly.
