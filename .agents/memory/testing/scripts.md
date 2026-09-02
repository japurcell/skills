---
coverage: Test and validation guidance for shell helper scripts under `scripts/`
---

# Shell Scripts - Testing

- Use syntax check plus the smallest relevant script test when one exists.
- Shell installer changes:
  - `bash -n scripts/install.sh && bash scripts/test-install.sh`
  - `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- Python helper module unit tests:
  - `python scripts/test_helpers.py`
- Hook-tree shell helper changes:
  - `bash scripts/test-repo-root.sh`
- For any `scripts/*.ps1` or PowerShell-specific install logic, use `.agents/memory/testing/powershell.md` instead of treating the check as generic shell validation.
- If a script primarily supports hooks, also run matching checks from `.agents/memory/testing/hooks.md`.
- If a script primarily supports a specific skill, run that skill's narrow validation path after the script check.
- In `scripts/test-common.sh`, keep `mock_bin` on `printf "%b\n"` so escaped newlines render into executable mock scripts.
- In `scripts/test-common.sh`, `write_required_skill_fixtures` writes mock skill files (`caveman`, `universal-guidelines`, `cli-compression`, `writing-great-skills`) to a test directory for skill hook tests.
