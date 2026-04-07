## HIGH: Authenticated command injection in the archive endpoint

- Location: `app.py:12`
- The pending change replaces `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)` with `subprocess.run(f"/usr/local/bin/archive-job --target {target}", shell=True, ...)`.
- `target` comes directly from `request.json["target"]`, so an authenticated caller can inject shell metacharacters such as `;`, `&&`, or command substitution and execute arbitrary commands on the server.
- This turns the `/archive` API into a remote code execution primitive for anyone holding a valid ops token. That is a direct integrity and confidentiality break, not just a job-routing bug.
- Remediation: keep `shell=False` and pass arguments as a list, or otherwise avoid shell interpolation entirely for user-controlled values.
