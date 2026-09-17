---
type: Testing Guidance
description: Repo-wide test layout, run commands, and shared authoring conventions; per-layer test guidance lives in testing/<area>.md
---

# Testing Strategy

Run `./scripts/test-all.py` for all maintained automated suites on macOS or Linux.
Use `--list` to inspect the explicit suite registry and `--help` for usage. For a
focused change, use the narrowest command below. The aggregate runner includes
its own CLI tests and excludes lint-only checks, formatting, live model evaluations,
archives, and generated fixtures. Its CLI contract is in [API Map](API_MAP.md#repository-test-runner).

## Shared rules

- Aggregate test prerequisites are `bash`, `python3`, `git`, `jq`, `flock`, `sqlite3`, and PowerShell 7+ (`pwsh`), plus ordinary Unix utilities and a writable checkout. The runner preflights tools and suite paths; missing dependencies are errors, not successful skips. Existing host-specific skips remain visible in child output.
- Formatting is separate from tests: `npx` with `oxfmt` for JS or TS hook formatting; `dotnet` for C# hook formatting.
- For interactive terminal work, prefer wrapping commands with `rtk`.
- Repo-source proof is not live proof. File reads and repo-local tests show repository state only.
- If installed behavior matters, run `./scripts/install.sh` before live checks because Copilot reads `~/.copilot/*` and Gemini reads `~/.gemini/*`.

## Route by area

- general provider hooks → `.agents/memory/testing/hooks.md`
- source auto-ingest hooks → `.agents/memory/testing/hooks-auto-ingest.md`
- hook observability and trace storage → `.agents/memory/testing/hooks-observability.md`
- skills (`skills/`) → `.agents/memory/testing/skills.md`
- scripts (`scripts/`) → `.agents/memory/testing/scripts.md`
- PowerShell scripts (`scripts/*.ps1`) → `.agents/memory/testing/powershell.md`

## Evidence discipline

- Static findings from file inspection or review output must stay labeled likely or candidate until backed by a concrete artifact.
- If asked for stronger certainty, gather at least one new artifact first: targeted search, exact file view, or narrow validation command.
- To prove a mode or branch is gone, prefer one targeted search over repeated whole-file rereads or duplicate validation loops.
