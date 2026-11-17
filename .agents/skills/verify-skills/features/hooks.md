# Provider hook configuration

## Sub-features

- Install Codex, Copilot, and Gemini hooks and registrations.
- Preserve unrelated existing registrations during refresh.
- Reject malformed configuration before destination mutation.

## How to get to it (user POV)

Run either installer, then start the provider client. Codex users review and trust the installed definition through `/hooks`.

## Driving it with Bash

Run the default installation journey. Read `$VERIFY_HOME/.codex/hooks.json`, `.copilot/hooks/hooks.json`, and `.gemini/settings.json`; retain the registrations and verify each installed script path exists. Verify owner-only config modes on POSIX and executable hook files. Inspect script contents as well as JSON validity.

Use `rtk proxy bash scripts/tests/installers/test-install.sh` for the maintained existing-registration and malformed-configuration fixtures; retain raw results and suite exit status. Use `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1` for the corresponding PowerShell suite. These exercise real installer commands against fixture assets, so label them as fixture coverage.

For native delivery, first obtain a separately isolated provider profile, then trigger its session-start flow and capture the actual required-skill context and provider logs. A missing client/profile is a blocked native journey, not passing hook-delivery evidence.

## Gotchas

- Directly invoking a hook script proves script behavior, not provider delivery.
- Do not refresh or drive the user's real provider profile for this disposable verification.
- Client trust is separate from installing valid registrations.
