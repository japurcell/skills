---
type: Agent Instruction
description: Start here before editing; select instructions by the task and skip unrelated branches.
---

# Instruction Routes

Read only matching rows. Follow a linked document's narrower branches when the task needs them; this is a routing map, not a reading list.

| Task | Read |
| --- | --- |
| Root documentation, installation workflow, or artifact retention | [Repository workflow](repo.md) |
| Selecting, pruning, or writing KB content; end-of-session doc pass | [Knowledge admission](knowledge-base.md) |
| Authoring or reviewing published or repo-local skills | [Skill conventions](skills.md) |
| Canonical custom agents or generated personal Codex agents | [Agent conventions](agents.md) |
| Shell/Python helper scripts or installers | [Script conventions](scripts.md) |
| PowerShell scripts or installer parity | [PowerShell conventions](powershell.md), plus shared [script conventions](scripts.md) |
| Hook implementation, registration, or runtime behavior | [Shared hook rules](hooks.md), then its matching provider or subsystem branch |
| Choosing or authoring validation | [Testing guidance](testing.md), then only the affected area's test route |

Formatting comes from [`.editorconfig`](../../.editorconfig). Use source, configuration, tests, and CLI help for ordinary layout and interface lookups. Retain non-obvious cross-file knowledge only when it passes admission.

For a specific unresolved limitation or external source, consult the optional [memory index](../memory/INDEX.md). Memory describes evidence; it does not create policy.
