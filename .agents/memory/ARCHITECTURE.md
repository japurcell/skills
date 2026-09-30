---
type: Agent Memory
description: Repo structure, install flows, and how top-level areas relate
---

# Architecture

## Top-level areas

| Path | Role | Main consumer |
| --- | --- | --- |
| `skills/` | Source of reusable task skills built around `SKILL.md` entry points. | Selected native repo/personal paths through `scripts/agent-assets.py`, or legacy `~/.agents/skills` copying through Bash/PowerShell installers. |
| `agents/` | Canonical Markdown source of custom agent definitions. | Selected native repo/personal adapters and legacy personal copies; Codex uses rendered TOML. |
| `references/` | Optional shared reference material shipped with this repo. | Selected catalog support files, or legacy `~/.agents/references` copying when that target exists. |
| `distribution/` | Explicit committed catalog of assets, dependencies, bundles and byte/checkout policies. | Selected-asset lifecycle engine; source availability differs from native client proof. |
| `.github/` | Repository-level Copilot config, including repo-local hooks. | Loaded directly from the workspace by Copilot |
| `.copilot/` | Copilot-specific instructions and hooks. | Installed to `~/.copilot/` |
| `.gemini/` | Gemini-specific instructions and hooks. | Installed to `~/.gemini/` |
| `.codex/` | Source for user-global Codex instructions and maintained startup, security, and command hooks. | `AGENTS.md` is copied to `~/.codex/AGENTS.md`; the maintained hooks are installed to `~/.codex/hooks/` and merged into `~/.codex/hooks.json`. It is not a custom-agent source. |
| `hooks/` | Canonical build-time source for generated provider-local Python hooks. | Rendered by `scripts/generate-hooks.py` into checked-in executable outputs; never imported across provider runtimes. |
| `scripts/` | Installers, importers, and targeted validation helpers. | Run from repo checkout |
| `.agents/` | Agent knowledge base with canonical agent-facing rules and durable repo facts. | Copilot/Gemini agents working in this repo |
| `docs/` | Version-controlled ADRs plus active research and effort plans that complement `.agents/` canonical guidance. | Repo readers and agents who need current project context or human decision history |
| `README.md`, `AGENTS.md` | Top-level human entry points that summarize the repo and point into `.agents/`. | Repo readers and agents |

## Main flows

### Source authoring flow

1. Edit source under `skills/`, `agents/`, `.github/`, `.copilot/`, `.gemini/`, `.codex/`, `references/`, or `scripts/`.
2. Run narrow validation for changed area from `.agents/memory/TESTING_STRATEGY.md` and any matching `testing/<area>.md` file.
3. Validate the installed representation in a disposable target through the selected lifecycle command or the affected legacy fixture. Native checks additionally require normal client trust and isolated state. A source edit alone does not refresh an installed copy; do not run a real-home refresh as an automated test. Legacy personal Codex instructions come from `.codex/AGENTS.md`, agents use `${CODEX_HOME:-$HOME/.codex}/agents`, and Copilot/Gemini use personal Markdown copies.

### Selected-asset distribution flow

`scripts/agent-assets.py` resolves catalog selection and required dependencies at an immutable committed source revision. It reads acquired source as bytes and renders native files/configuration through trusted command-checkout code. Team mode materializes selected payloads and paired records for review and commit; a consuming clone receives those payloads without source acquisition. Private repository and personal modes use the same ownership/lifecycle engine with different layouts.

Explicit update follows saved branch or pin policy, preserves unchanged-upstream local edits, and prunes only authenticated unchanged unused ownership. Current-record restore uses the recorded revision. Strict status audits installed bytes, effective checkout policy and record agreement offline before any repair; it does not authenticate an adversarial rewrite of the entire committed authority. Native settings retain unrelated entries. POSIX writers pin parent descriptors and retain an interrupted-operation journal; Windows mutation/recovery remains unsupported pending a safe native backend. File/protocol acceptance does not establish native trust, discovery or event delivery. See [public interfaces](API_MAP.md), [script rules](../instructions/scripts.md) and [usage](../../docs/agent-asset-installer/usage.md).

### Generated provider-hook flow

1. Change canonical build-time source under `hooks/`, never a provider-local file carrying the generated ownership marker.
2. Run `python3 scripts/generate-hooks.py --write`, then `python3 scripts/generate-hooks.py --check` and `python3 scripts/test-generate-hooks.py`.
3. Commit the refreshed executable provider-local outputs. Before copying them, installers run the generator's read-only `--check` preflight; they never invoke `--write` and stop before destination mutation when freshness fails.

### Addy import flow

`scripts/addy-install.sh` is upstream-ingestion path. It syncs `../addy-agent-skills`, copies selected upstream agents, skills, and top-level references into this repository, prefixes imported names with `addy-`, and refreshes `.addy-skills` with source skill names that were installed.

`scripts/import-skill-repos.sh` is separate multi-source importer. It refreshes selected skills from upstream repositories, including `web-accessibility`, `web-best-practices`, and `web-performance` from `addyosmani/web-quality-skills`.

### Documentation flow

- `README.md` and `AGENTS.md` stay as short top-level entry points.
- Durable agent-facing rules and repo facts belong in `.agents/instructions/` and `.agents/memory/`.
- Active research and planning artifacts that need version history belong under a focused `docs/<effort>/` subtree; transient working state remains in `.agents/scratchpad/`. After an effort finishes, import unique durable agent knowledge into `.agents/`, remove completed research and planning artifacts unless historical retention was requested, and retain ADRs by default.
- Keep top-level summaries aligned with `.agents/` instead of maintaining parallel long-form copies.

## Boundaries

- Treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- Treat `skills/archive/` as historical reference, not primary authoring surface.
- Treat `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` as fixtures unless task explicitly targets them.
- `.agents/sources/` and most of `.agents/skills/` are not normal edit targets; repository-maintained documentation work stays in `.agents/instructions/` and `.agents/memory/`. Exception: `.agents/skills/ingest-source/SKILL.md` is the canonical repo-local auto-ingest recovery skill and is maintained with the pending-ingest hook flow.
