---
type: Testing Guidance
description: Test and validation guidance for PowerShell scripts under `scripts/`
---

# PowerShell - Testing

- Use syntax check plus narrow script validation when one exists.
- Installer changes:
  - `pwsh -NoProfile -File scripts/test-install.ps1` (requires `pwsh` on PATH; covers skill excludes/pruning, the full Gemini tree copy, link handling, missing-source stderr behavior, and non-Windows exact mode assertions; `Test-JunctionHandling` skips when host cannot create junctions, so run once on a Windows-capable host for junction-specific proof)
- Hook-tree shell helper changes:
  - `bash scripts/test-repo-root.sh`
- If a script primarily supports hooks, also run matching checks from `.agents/memory/testing/hooks.md`.
- If a script primarily supports a specific skill, run that skill's narrow validation path after the script check.
- In `scripts/test-common.sh`, keep `mock_bin` on `printf "%b\n"` so escaped newlines render into executable mock scripts.
- In `scripts/test-common.sh`, `write_required_skill_fixtures` writes mock skill files (`caveman`, `universal-guidelines`, `cli-compression`, `writing-great-skills`) to a test directory for skill hook tests.

## Scope note

This file covers PowerShell-specific validation. Shell-focused script checks remain in `.agents/memory/testing/scripts.md`.
