---
type: Testing Guidance
description: Test and validation guidance for PowerShell scripts under `scripts/`
---

# PowerShell - Testing

- Use syntax check plus narrow script validation when one exists.
- RTK native Windows proof: `pwsh -NoProfile -File scripts/test-rtk-stable-windows.ps1` in the dedicated Windows workflow. It checks old-version preflight, the `%APPDATA%` TOML path, backup/idempotence, and real stable RTK diagnostics in a disposable profile. The workflow installs official `rtk-ai.rtk` with winget, requires stable version 0.50.0 or newer, and checks the `copilot` and `gemini` hook processors; the repository installer does not install RTK.
- Installer changes:
  - `pwsh -NoProfile -File scripts/test-install.ps1` (requires `pwsh` on PATH; covers skill excludes/pruning, the full Gemini tree copy, link handling, generated-hook freshness preflight, missing-source stderr behavior, and non-Windows exact mode assertions; `Test-JunctionHandling` skips when host cannot create junctions, so run once on a Windows-capable host for junction-specific proof)
  - The disposable-home provider refresh cases cover preservation of old and custom hook entries, nested Gemini settings, idempotence, fresh absence, malformed/ambiguous JSON, hard-linked destination safety, and linked parent refusal before mutation. Linked-parent coverage uses symlinks on POSIX and junctions on Windows when the host permits them.
  - The same suite covers Codex custom-agent conversion before copy operations, generated TOML decoding, idempotence, malformed-source early failure, `$env:CODEX_HOME` destination selection, and replacement of `$HOME/.codex/AGENTS.md` from `.codex/AGENTS.md`.
- Generated secret-scanner capture: `pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` on native Windows; the script skips on other hosts. It is registered in `.github/workflows/ready-ideas-windows.yml` and exercises all three generated providers through JSON input with `git.cmd` failure, descendant, size, malformed output, temporary-file failure, committed-repository HEAD failure, and genuine no-HEAD cases. It checks for `tmp*` files immediately after each hook returns and repeats Gemini descendant and oversized cases five extra times each. A non-Windows skip is syntax evidence only.
- Repository OKF envelopes: `pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1` on native Windows; it checks all three project adapters, Windows rerun text, and Codex registered-command resolution from a nested directory. The script skips on other hosts.

## Scope note

This file covers PowerShell-specific validation. Apply shared helper, hook, and skill routing from [Shell Scripts - Testing](scripts.md).
