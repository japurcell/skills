---
type: Known Issue
description: Real shell-specific runtime gotchas; PowerShell-specific issues live in the separate pwsh doc
---

# Shell Scripts - Known Issues

- Keep shell and PowerShell guidance separate so agents load only the rules relevant to the current task.
- `bash`-specific logic should not silently rely on POSIX shell behavior. `[[ ... ]]` is bash-only; use portable `[ ... ]` or explicit bash conditions when the script is intentionally bash-specific.
- `grep -R` follows symlinks by default, so shell checks that search repo trees can produce false positives through preserved symlinks. Prefer `find <tree> -type f -exec grep -l <needle> {} +` when proving "no regular file under the tree contains X".
- Temporary files must be created under a controlled path and cleaned up with `trap`/`rm -f` so failed shell scripts do not leave stale state behind; do not rely on ad hoc `mktemp` usage without cleanup logic.
- Checking only `yaml.__version__` does not prove the OKF linter loaded its pinned parser: a matching site package can mask an absent vendor tree. Also verify that `yaml.__file__` resolves below `scripts/vendor/yaml/`.
- On case-insensitive filesystems, an OKF fixture named `index.md` can overwrite an existing `INDEX.md` in the same directory. Remove the canonical copy before creating the reserved-name case, then assert the intended diagnostic.
- OKF Markdown masking must scan comments, fences, and inline code left-to-right so the first active construct owns contained delimiters. Replace ignored characters with spaces while preserving newlines so later diagnostic columns do not shift. Valid unclosed fences and comments extend through EOF; backtick fence info strings containing backticks are not valid openers; inline code closes only on an exact-length backtick run.
- Regex-only Markdown link extraction misses balanced labels, balanced or escaped parentheses, and angle-bracket destinations. Preserve the deterministic scanner and its public-CLI regression cases when changing link validation.
- Unquoted variable expansion is a common shell failure mode in loops and path checks. Prefer `"$var"` for untrusted values and avoid building commands from unescaped string fragments.
- Python can replace a chosen broken-pipe exit code with `120` while flushing buffered output at shutdown. `scripts/test-all.py` flushes inside its exception boundary and redirects failed output descriptors to the null device before returning `141`.
- A cancelled suite leader can exit while descendants still run. The aggregate runner owns a separate process group per child and checks that group during bounded cleanup even after reaping the leader. Descendants that deliberately start a new session or process group are outside that group.
- `scripts/install.sh` derives most destinations from `$HOME` and has no general destination override. It invokes Codex-agent conversion first, so a read-only later skill, Copilot, Gemini, reference, or hook target can leave successfully refreshed Codex TOML while stopping the remaining copies. In that environment, report exactly which phase completed, validate source behavior, and leave the remaining refresh for a writable user shell; do not repurpose `HOME`.
- If a problem is really `pwsh`-specific, keep it in `.agents/memory/known-issues/powershell.md`; do not dilute the shell doc with PowerShell details.
