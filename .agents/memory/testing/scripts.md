---
type: Testing Guidance
description: Test and validation guidance for shell helper scripts under `scripts/`
---

# Shell Scripts - Testing

- Use syntax check plus the smallest relevant script test when one exists.
- Aggregate runner changes: `python3 scripts/test_test_all.py`. These public-CLI tests need Python and Bash, not the full suite toolchain. They copy the runner into temporary checkouts, substitute suite/tool executables at the process boundary, and cover registry completeness, preflight failures, stdin/stream separation, aggregate exits, broken pipes, and cancellation. Full integration is `./scripts/test-all.py` after its prerequisites are available.
- Cancellation fixtures inherit output pipes. A successful bounded `communicate()` requires EOF from descendants as well as the runner; cleanup-only kills happen after assertions and cannot make a leaked descendant pass. The suite verifies both graceful shutdown and forced termination after the suite leader exits.
- Shell installer changes:
  - `bash -n scripts/install.sh && bash scripts/test-install.sh`
  - Codex custom-agent conversion: `python3 scripts/test-codex-agents.py`, then `bash -n scripts/install.sh && bash scripts/test-install.sh`; the fixture suite parses generated TOML, checks exact instruction preservation, managed cleanup, and `CODEX_HOME` selection.
  - `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- Python helper module unit tests:
  - `python scripts/test_helpers.py`
- OKF linter changes:
  - `bash -n scripts/test-okf-lint.sh && bash scripts/test-okf-lint.sh`
  - The suite copies `scripts/fixtures/okf-valid-repo/` into a fresh `mktemp` directory for each public-CLI case. Do not derive uniqueness from a shell counter mutated inside command substitution; that mutation runs in a subshell and does not persist.
  - Exercise dependency-failure cases from an isolated copied linter/vendor layout. Never move or hide the live `scripts/vendor/yaml/` tree during a test.
  - Keep assertions at the public `./scripts/lint-okf.py [--format human|json]` seam, including exact one-based diagnostic locations and exit codes.
  - Keep cross-platform destination cases for Windows drive-rooted and UNC paths, source-summary footnotes, and both nesting directions among HTML comments, fenced code, and exact-run inline code.
- Hook-tree shell helper changes:
  - `bash scripts/test-repo-root.sh`
- For any `scripts/*.ps1` or PowerShell-specific install logic, use `.agents/memory/testing/powershell.md` instead of treating the check as generic shell validation.
- If a script primarily supports hooks, also run matching checks from `.agents/memory/testing/hooks.md`.
- If a script primarily supports a specific skill, run that skill's narrow validation path after the script check.
- In `scripts/test-common.sh`, keep `mock_bin` on `printf "%b\n"` so escaped newlines render into executable mock scripts.
- In `scripts/test-common.sh`, `write_required_skill_fixtures` writes mock skill files (`caveman`, `universal-guidelines`, `cli-compression`, `writing-great-skills`) to a test directory for skill hook tests.
