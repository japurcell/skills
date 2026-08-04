---
coverage: Repo-wide test layout, run commands, and shared authoring conventions; per-layer test guidance lives in testing/<area>.md
---

# Testing Strategy

Run narrowest command that exercises changed area. There is no single repo-wide
test runner.

## Shared rules

- Install prerequisites before area checks: `bash`, `python3`, `git`, plus `jq` and `flock` for hooks; `npx` with `oxfmt` for JS or TS hook formatting; `dotnet` for C# hook formatting.
- For interactive terminal work, prefer wrapping commands with `rtk`.
- Repo-source proof is not live proof. File reads and repo-local tests show repository state only.
- If installed behavior matters, run `./scripts/install.sh` before live checks because Copilot reads `~/.copilot/*` and Gemini reads `~/.gemini/*`.

## Route by area

- hooks (`.copilot/hooks`, `.gemini/hooks`) → `.agents/memory/testing/hooks.md`
- skills (`skills/`) → `.agents/memory/testing/skills.md`
- scripts (`scripts/`) → `.agents/memory/testing/scripts.md`

## Evidence discipline

- Static findings from file inspection or review output must stay labeled likely or candidate until backed by a concrete artifact.
- If asked for stronger certainty, gather at least one new artifact first: targeted search, exact file view, or narrow validation command.
- To prove a mode or branch is gone, prefer one targeted search over repeated whole-file rereads or duplicate validation loops.
