# Scripts and maintained tests

Run commands from the repository root. Public commands stay in `scripts/`; private maintained test suites and their support live under `scripts/tests/`. The suite registry in `test-all.py` is explicit. Runtime commands do not discover tests.

Use `python3 scripts/test-all.py --list` to inspect the maintained suite list and `python3 scripts/test-all.py` for the full aggregate. Focused commands below run only the relevant evidence. `scripts/tests/support/` contains shared test fixtures, not a public API.

## Install and refresh

Public entrypoints: `scripts/install.sh`, `scripts/install.ps1`, `scripts/install-codex-hooks.py`, and `scripts/install-codex-agents.py`. For repository gates and the secret scanner, use `scripts/install-repo-gates.py` and `scripts/install-scan-secrets.py`.

`hooks/manifest.py` lists the checked-in runtime files rendered from canonical family sources under `hooks/`. For those declared targets, regenerate with `python3 scripts/generate-hooks.py --write` and verify freshness with `python3 scripts/generate-hooks.py --check`. This ownership rule applies only to manifest targets, not every provider hook file.

Focused installer evidence: `bash scripts/tests/installers/test-install.sh`, `pwsh scripts/tests/installers/test-install.ps1`, `python3 scripts/tests/installers/test-install-codex-hooks.py`, and `python3 scripts/tests/installers/test-codex-agents.py`. Gate and scanner installation checks are `python3 scripts/tests/scanner/test-install-repo-gates.py` and `python3 scripts/tests/scanner/test-install-scan-secrets.py`. Installer test fixtures and private shared helpers stay in `scripts/tests/`.

## Hook behavior and generated providers

Edit canonical hook sources under `hooks/` and regenerate provider outputs with the command above; do not hand-edit generated copies. Provider suites are `bash scripts/tests/hooks/test-hooks-startup.sh`, `bash scripts/tests/hooks/test-hooks-rtk.sh`, `bash scripts/tests/hooks/test-hooks-observability.sh`, and their Codex/Gemini counterparts in the same directory. Generation and brain-hook checks are `python3 scripts/tests/hooks/test-generate-hooks.py` and `python3 scripts/tests/hooks/test-brain-hooks.py`.

The canonical source owns runtime behavior for each manifest target. Provider-local generated scripts must remain standalone. Gemini's SessionStart required-skill entrypoint is provider-authored at `.gemini/hooks/scripts/skill-context-injector.py`; the installers copy the checked-in `.gemini/hooks` tree. It imports shared audit and skill-loading helpers from manifest-owned families `hooks/families/audit.py` and `hooks/families/common.py`. The generator freshness check covers those helper outputs, not the entrypoint itself. Its focused behavior suite is `bash scripts/tests/hooks/test-gemini-hooks-startup.sh`. Private hook fixtures and helpers are alongside the maintained suites; shared cross-suite shell helpers are in `scripts/tests/support/`.

## Secret scanner and repository gates

The public scanner is `scripts/scan-secrets.py`; installation and gate entrypoints remain public scripts at the top level. Scanner suites and private fixtures live under `scripts/tests/scanner/`. Focused checks include `python3 scripts/tests/scanner/test-scan-secrets-cli.py`, `python3 scripts/tests/scanner/test-scan-secrets-git-gates.py`, `python3 scripts/tests/scanner/test-scan-secrets-status.py`, and `python3 scripts/tests/scanner/test-scan-secrets-lifecycle.py`. Provider integrations have focused suites in the same directory.

The real Git LFS cases require Git LFS on `PATH`; the verified environment used 3.8.0. Set `TEST_GIT_LFS` to an absolute Git LFS executable when it is not on `PATH`. Fixture-copy tests and scanner-only support remain private under `scripts/tests/scanner/`.

Several scanner/security suites inspect or stop child processes, bind loopback sockets, or query `sysctl kern.clockrate`. Restricted sandboxes that deny `/bin/ps`, loopback binds, or this sysctl query can fail before the behavior under test runs. Use a test environment that permits these host checks; do not skip the affected cases.

## Tool Guardian and security reporting

Canonical Guardian policy and hook behavior are owned by `hooks/`; generated provider outputs follow the generation rule above. Guardian policy suites are in `scripts/tests/guardian/`, including `bash scripts/tests/guardian/test-codex-hooks-tool-guard.sh` and `python3 scripts/tests/guardian/test-security-banners.py`. The banner suite exercises Guardian output and fixtures. `python3 scripts/tests/hooks/test-security-reporting.py` covers cross-cutting scanner and Guardian reporting, so it stays with hook integration evidence.

Guardian fixtures and `tool_guard_test_support.py` are private test support in the Guardian directory. Do not move public installed helper names or make installed hooks depend on test-only modules.

## Hook evidence and maintenance

The public evidence commands `scripts/benchmark-high-rate-hooks.py` and `scripts/verify-hook-release.py` have focused suites under `scripts/tests/hooks/`. Run those suites directly when changing benchmark or release verification behavior. Their test fixtures and helpers remain private to the test tree.

Tooling and shared test harness checks live in `scripts/tests/tooling/` and `scripts/tests/runner/`. For example, run `bash scripts/tests/tooling/test-cleanup-skill-workspaces.sh`, `python3 scripts/tests/tooling/test_helpers.py`, and `python3 scripts/tests/runner/test_test_all.py`. The harness owns the explicit suite list; `scripts/tests/runner/test_test_all.py` independently checks that maintained suites are represented.

The repo-maintenance commands `scripts/import-skill-repos.sh` and `scripts/pull-skill-repos.sh` are human-only. Agents should use targeted verification and maintained test commands instead.

## Platform evidence

POSIX shell checks run in the supported POSIX environments. PowerShell suites under `scripts/tests/` and the Windows workflow provide native Windows evidence; POSIX results do not replace those checks. Use the direct PowerShell command shown in the relevant suite or workflow for Windows-only installer, provider, scanner, lifecycle, and RTK behavior.

## Related guidance

- [Script and installer ownership](../brain/codebase/scripts-and-installers.md)
- [Testing routes and evidence limits](../brain/codebase/testing.md)
- [Hook testing](../brain/codebase/hook-testing.md)
- [Security testing](../brain/codebase/security-testing.md)
- [Installer testing](../brain/codebase/installer-testing.md)
