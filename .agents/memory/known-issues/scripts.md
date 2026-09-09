---
coverage: Real shell-specific runtime gotchas; PowerShell-specific issues live in the separate pwsh doc
---

# Shell Scripts - Known Issues

- Keep shell and PowerShell guidance separate so agents load only the rules relevant to the current task.
- `bash`-specific logic should not silently rely on POSIX shell behavior. `[[ ... ]]` is bash-only; use portable `[ ... ]` or explicit bash conditions when the script is intentionally bash-specific.
- `grep -R` follows symlinks by default, so shell checks that search repo trees can produce false positives through preserved symlinks. Prefer `find <tree> -type f -exec grep -l <needle> {} +` when proving "no regular file under the tree contains X".
- Temporary files must be created under a controlled path and cleaned up with `trap`/`rm -f` so failed shell scripts do not leave stale state behind; do not rely on ad hoc `mktemp` usage without cleanup logic.
- Unquoted variable expansion is a common shell failure mode in loops and path checks. Prefer `"$var"` for untrusted values and avoid building commands from unescaped string fragments.
- `scripts/install.sh` derives every destination from `$HOME` and has no destination override. In agent environments where those installation trees are read-only, validate the source change, report that installed copies were not refreshed, and leave installation for a writable user shell; do not repurpose `HOME`.
- If a problem is really `pwsh`-specific, keep it in `.agents/memory/known-issues/powershell.md`; do not dilute the shell doc with PowerShell details.
