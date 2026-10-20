# PowerShell installer rules

- Use case-sensitive literal comparisons where names or signatures are exact contracts.
- Resolve one application through `Get-Command`; do not accidentally combine several candidate paths.
- Preserve Bash/PowerShell install parity, including Codex agent generation and exact hook ownership.
- Refuse symbolic links, junctions, and reparse-point destinations before copying or changing permissions.
- Test homes must isolate Windows home/config variables, including USERPROFILE, APPDATA, and LOCALAPPDATA; use disposable test destinations.
- Native Windows proves junction, ACL, job-object, and cmd/PowerShell quoting behavior. Non-Windows skips are only syntax or registration evidence.

Evidence: [PowerShell installer](../../scripts/install.ps1), [installer suite](../../scripts/test-install.ps1), checked 2026-10-20. Recheck copying, launch resolution, or environment isolation changes.
