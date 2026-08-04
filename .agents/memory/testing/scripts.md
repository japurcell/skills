---
coverage: Test and validation guidance for repository helper scripts under `scripts/`
---

# Scripts - Testing

- Use syntax check plus narrow script test when one exists.
- Installer changes:
  - `bash -n scripts/install.sh && bash scripts/test-install.sh`
  - `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- If a script primarily supports hooks, also run matching checks from `.agents/memory/testing/hooks.md`.
- If a script primarily supports a specific skill, run that skill's narrow validation path after the script check.
- In `scripts/test-common.sh`, keep `mock_bin` on `printf "%b\n"` so escaped newlines render into executable mock scripts.
