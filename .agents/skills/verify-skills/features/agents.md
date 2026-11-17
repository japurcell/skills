# Custom agent installation

## Sub-features

- Copy canonical Markdown agents for Gemini and Copilot.
- Generate Codex TOML and an ownership manifest.
- Honor an alternate CODEX_HOME for generated agents.

## How to get to it (user POV)

Run either installer, then select an installed custom agent in the corresponding client.

## Driving it with Bash

Run the default installation journey. Compare each top-level `agents/*.md` with its copies in `$VERIFY_HOME/.gemini/agents` and `.copilot/agents`. Parse every generated `.codex/agents/*.toml`; match its `developer_instructions` exactly to the canonical Markdown body after frontmatter. Capture names and comparison results. Inspect `.skills-repo-agents.json` in the generated agents directory.

For the alternate destination, set CODEX_HOME to `$VERIFY_HOME/alternate-codex`, rerun, and prove TOML and manifest exist there. Hook configuration still lives in `$VERIFY_HOME/.codex`; record that distinction. Supplement ownership/stale-file cases with `rtk proxy python3 scripts/tests/installers/test-codex-agents.py`. Repeat with the PowerShell installer for parity.

## Gotchas

- Repository `.codex/` is not the canonical custom-agent source.
- File proof does not establish client discovery or successful agent selection. That branch requires an isolated native provider session; report it unverified when unavailable.
- Never edit generated personal TOML as the source of a fix.
