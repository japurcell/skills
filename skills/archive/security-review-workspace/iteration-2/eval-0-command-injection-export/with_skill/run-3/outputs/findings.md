# Vuln 1: Shell command injection in archive target handling: `app.py:14`

- Severity: HIGH
- Category: Command injection
- Description: The pending diff changes `subprocess.run` from an argument array to a shell command string and enables `shell=True` while still interpolating attacker-controlled `request.json["target"]` directly into the command. Any caller who can hit this endpoint with a valid `X-Ops-Token` can supply shell metacharacters such as `;`, `&&`, or command substitution to execute arbitrary commands as the Flask service account. The previous version passed `target` as a separate argv element, so this RCE path is introduced by the diff.
- Recommendation: Remove `shell=True` and pass the command as a list again, for example `["/usr/local/bin/archive-job", "--target", target]`. If shell invocation is truly required, quote the untrusted value with a strict allowlist, but avoiding the shell is the correct minimal fix here.
