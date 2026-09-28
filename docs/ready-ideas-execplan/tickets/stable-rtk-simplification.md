# Stable RTK Simplification

**Type:** grilling
**Status:** closed
**Blocked By:** rtk-050-release-facts.md
**Research Dir:** none

## Question

Given stable RTK 0.50.0 support, where should command-scoped warning suppression live for Copilot, Gemini, and Codex, and which prerelease installer, receipt, explicit-command adapter, launcher, registration, tests, and documentation should disappear? Decide how to preserve command behavior, user terminal behavior, and safe migration of installed copies.

---

## Resolution

Use a normal stable RTK installation at version 0.50.0 or newer on each supported platform. The user already updated this Mac's PATH RTK, and `rtk --version` returned `rtk 0.50.0`. Before either `scripts/install.sh` or `scripts/install.ps1` changes any installed file, require a suitable RTK binary and stop with upgrade instructions if it is absent or older. Do not install another RTK binary through this repository.

Both installers must manage the user's persistent RTK configuration. On each run, set only `[hooks] suppress_hook_warning = true`, preserving every unrelated setting and backing up an existing file before a semantic change. An existing `false` is replaced with `true`; an unchanged configuration must remain untouched. Refuse unsafe or ambiguous edits rather than damaging user configuration. RTK 0.50.0 documents macOS `~/Library/Application Support/rtk/config.toml` and Linux `~/.config/rtk/config.toml`; the tagged source resolves Windows to `%APPDATA%\rtk\config.toml`. This account-wide setting also suppresses the missing-hook advisory in ordinary terminal sessions, which the user accepted. `RTK_SUPPRESS_HOOK_WARNING=0` can override the setting for one process. Keep RTK's outdated-hook notice and all other diagnostics visible.

Keep the Copilot and Gemini automatic RTK forwarders and their registrations. They pass provider tool events to `rtk hook copilot` or `rtk hook gemini`, which enables automatic RTK routing of ordinary tool commands. The Copilot forwarder also converts RTK's `ask` decision to `allow`; the Gemini forwarder passes it through. Codex has no automatic RTK forwarder and continues to use explicit `rtk` commands.

Delete the prerelease-specific installer, receipt verification, explicit-command adapters, launchers, their generated targets and registrations, and obsolete tests. In particular, remove the prerelease portions of `hooks/families/rtk.py`, generated `rtk-explicit-*` and `rtk-agent-launcher.py` files, `scripts/install-rtk-prerelease.py`, and the relevant entries in `hooks/manifest.py`, provider hook configuration, Codex owned-hook lists, and Bash/PowerShell installers. Keep automatic-forwarder source and tests. Update the current README, provider instructions, `.agents/` hook and script guidance, file/API maps, testing docs, ExecPlan, and Windows checklist where they describe the removed path. Historical tickets remain historical.

Migrate installed copies safely. Delete the side-by-side prerelease binary and receipt under `~/.agents/rtk/dev-0.50.0-rc.451/` and any installed explicit adapter or launcher only after matching repository ownership and expected content or receipt hashes. Leave unknown or modified files in place and report them for manual review. Current read-only inventory found a matching prerelease binary and receipt but no installed explicit adapters or launchers; installed Copilot and Gemini automatic forwarders match the checkout and must remain.

Acceptance must verify installer preflight and idempotence, config preservation and backup, supported platform paths, exact installed-file cleanup, and absence of obsolete registrations. With installed RTK 0.50.0 or newer, an explicit agent `rtk` command must omit only the missing-hook advisory while preserving arguments, stdout, stderr diagnostics, and exit status. Check automatic forwarder behavior separately. Do not add regression tests for deleted features; remove obsolete tests and test retained behavior and migration instead.
