# Vuln 1: Authenticated command injection in archive handler: `app.py:15`

- Severity: HIGH
- Category: Command injection
- Description: The pending diff changed `subprocess.run()` from an argument list to a shell-interpreted command string while still embedding `request.json["target"]` directly into the command. An attacker who can reach this endpoint with a valid `X-Ops-Token` can supply shell metacharacters such as `;`, `&&`, or backticks in `target` and execute arbitrary commands as the Flask service user, turning a normal archive request into remote code execution.
- Recommendation: Remove `shell=True` and pass the executable and user input as a list, for example `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)`, or apply strict allowlist validation before invoking any shell.
