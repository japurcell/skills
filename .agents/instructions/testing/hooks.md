---
type: Agent Instruction
description: Select source suites for hook runtime and registration changes; live delivery and security have separate routes.
---

# Hook Tests

## Repo checks

For generated hook changes, run `rtk proxy python3 scripts/generate-hooks.py --check` before and after the affected suites, plus `rtk proxy python3 scripts/test-generate-hooks.py`. Use `--write` only to refresh manifest-owned output. Keep generator and installer fixture mutations serialized. Pause all repository edits during the generator suite: its read-only assertions compare whole-checkout snapshots, including unrelated files.

Select the affected provider and behavior; do not run every row for a documentation-only change:

| Behavior | Commands from the repository root |
| --- | --- |
| Required skills and startup | `rtk proxy bash scripts/test-hooks-startup.sh`, `rtk proxy bash scripts/test-gemini-hooks-startup.sh`, `rtk proxy bash scripts/test-codex-hooks-startup.sh` |
| Project OKF adapters | `rtk proxy bash scripts/test-hooks-okf-lint.sh`, `rtk proxy bash scripts/test-gemini-hooks-okf-lint.sh`, `rtk proxy bash scripts/test-codex-repository-okf.sh` |
| Shared Python helpers | `rtk proxy python3 scripts/test_helpers.py` |
| RTK configuration and forwarding | `rtk proxy python3 scripts/test-rtk-stable.py`, `rtk proxy bash scripts/test-hooks-rtk.sh`, `rtk proxy bash scripts/test-gemini-hooks-rtk.sh` |
| Installer refresh | [Script tests](scripts.md), or [PowerShell tests](powershell.md) |
| Scanning, pending summaries, or coordinator ordering | [Source ingestion](hooks-auto-ingest.md) |
| Logs, traces, transcripts, or maintenance | [Observability](hooks-observability.md) |
| Security decisions, scanner capture, or latency | [Security](hooks-security.md) |

## Fixture and registration obligations

- Keep test homes, audit logs, SQLite files, and observation output in disposable directories. Reuse `scripts/test-common.sh` helpers. Fixture-local environment changes must not mutate the real user home.
- Assert exact Bash and PowerShell command paths for Copilot registrations. Assert required relative handler order rather than fixed array indexes where intervening handlers are permitted.
- Keep Copilot auto-ingest repo-local. Keep OKF out of global configs and post-tool events. Preserve one Copilot stop coordinator and source-ingest-first ordering for Gemini `AfterAgent`.
- Retain public JSON-envelope checks for pass, denial, retry, incomplete results, safe counts, UTF-8, open stdin, buffered trailing data, and high-rate pass silence. Adapter fixtures must reject an external checkout's decoy linter and preserve independent source-ingest and OKF reasons.
- Keep multi-skill startup fixtures independent of optional installed skills. Gemini's missing-skill case intentionally emits a hard-stop diagnostic; evaluate its assertions and exit status.
- For Codex, preserve raw-file versus final-context limits, removable frontmatter, containment, audit-link defenses, and temporary-home registration resolution. Installed non-managed hooks require trust review through `/hooks`.
- Keep native Windows cases in their dedicated workflow. `test-lifecycle-messages-windows.ps1`, `test-repository-okf-windows.ps1`, `test-codex-hooks-windows.ps1`, and `test-rtk-stable-windows.ps1` require Windows for behavioral proof. A skip elsewhere is only syntax/registration evidence.

For provider-visible output or actual event delivery, follow [live-hook testing](hooks-live.md). Source tests do not establish deployed behavior.
