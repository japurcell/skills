# Repository State Guardrails

**Type:** grilling
**Status:** open
**Blocked By:** provider-hook-capabilities.md
**Research Dir:** none

## Question

Which guardrails should prevent agent actions from damaging `.git/` metadata or overwriting uncommitted user edits, and where can those guardrails reliably run? Decide protection for direct tool writes, arbitrary Python or PowerShell scripts, and destructive Git checkout or restore commands; state limits and the required diff review workflow.

---
