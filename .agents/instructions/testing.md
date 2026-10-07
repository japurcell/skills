---
type: Agent Instruction
description: Choose validation for the changed area; distinguish repository checks from installed and platform evidence.
---

# Testing Guidance

Run the narrowest existing suite that covers the change. `rtk proxy python3 scripts/test-all.py --list` lists maintained commands; its `--help` describes invocation. Use `rtk proxy python3 scripts/test-all.py` for an aggregate run when warranted. Missing prerequisites are errors, not passing skips. Formatting and live model evaluations are separate checks.

| Changed area | Test instructions |
| --- | --- |
| Shared hook runtime or registration | [Hooks](testing/hooks.md) |
| Source scanning, summaries, manifests, or pending gates | [Source ingestion](testing/hooks-auto-ingest.md) |
| Emitters, traces, transcripts, audit logs, or maintenance | [Observability](testing/hooks-observability.md) |
| Tool Guardian, scanner security, or performance acceptance | [Hook security](testing/hooks-security.md) |
| Installed provider event delivery or visible messages | [Live hooks](testing/hooks-live.md) |
| Skills, graders, or evaluation artifacts | [Skills](testing/skills.md) |
| Shell/Python scripts and installers | [Scripts](testing/scripts.md) |
| PowerShell scripts or native Windows installer proof | [PowerShell](testing/powershell.md) |

Repository tests prove source behavior. Installed copies, provider delivery, and native Windows execution require their own evidence. Honor task-specific installation ownership; see [repository workflow](repo.md). A platform skip is not proof of that platform.

Label hypotheses as candidates until supported by an artifact. When stronger certainty is requested, obtain a new relevant file view, search result, or validation result. Use one targeted search to verify a removed branch; repeat tests only when changed source, failures, or unresolved concerns justify it.
