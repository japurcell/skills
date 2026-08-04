---
coverage: Rules and conventions for repository helper scripts under `scripts/`
---

# Scripts Conventions

- Follow existing shebang style: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- Prefer standard-library solutions unless an existing script already implies dependency use.
- Run syntax check plus narrow script validation from `.agents/memory/testing/scripts.md`.
