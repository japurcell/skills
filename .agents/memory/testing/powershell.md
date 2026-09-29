---
type: Testing Guidance
description: Test and validation guidance for PowerShell scripts under `scripts/`
---

# PowerShell - Testing

- Use syntax check plus narrow script validation when one exists.
- RTK native Windows proof: `pwsh -NoProfile -File scripts/test-rtk-stable-windows.ps1` in the dedicated Windows workflow. It checks old-version preflight, the `%APPDATA%` TOML path, backup/idempotence, and real stable RTK diagnostics in a disposable profile. The workflow installs RTK; the repository installer does not.
- Installer changes:
  - `pwsh -NoProfile -File scripts/test-install.ps1` (requires `pwsh` on PATH; covers skill excludes/pruning, the full Gemini tree copy, link handling, generated-hook freshness preflight, missing-source stderr behavior, and non-Windows exact mode assertions; `Test-JunctionHandling` skips when host cannot create junctions, so run once on a Windows-capable host for junction-specific proof)
  - The same suite covers Codex custom-agent conversion before copy operations, generated TOML decoding, idempotence, malformed-source early failure, `$env:CODEX_HOME` destination selection, and replacement of `$HOME/.codex/AGENTS.md` from `.codex/AGENTS.md`.
- Generated secret-scanner capture: `pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` on native Windows; the script skips on other hosts. It is registered in `.github/workflows/ready-ideas-windows.yml` and exercises all three generated providers through JSON input with `git.cmd` failure, descendant, size, malformed output, temporary-file failure, and no-HEAD cases.

## Scope note

This file covers PowerShell-specific validation. Apply shared helper, hook, and skill routing from [Shell Scripts - Testing](scripts.md).
