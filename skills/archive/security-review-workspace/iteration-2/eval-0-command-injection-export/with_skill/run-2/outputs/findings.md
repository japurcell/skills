# Vuln 1: Command injection in archive job launch: `app.py:15`

- Severity: HIGH
- Category: Command injection
- Description: The changed `/archive` handler now interpolates the request-controlled `target` value directly into a shell command string and executes it with `shell=True`. Any caller that can reach this endpoint with a valid ops token can inject shell metacharacters such as `;`, `&&`, or backticks in `target` to execute arbitrary commands on the server instead of just queuing an archive job.
- Recommendation: Stop invoking the shell for this path and pass arguments as a list, e.g. `subprocess.run(["/usr/local/bin/archive-job", "--target", target], ...)`. If additional validation is intended, enforce an allowlist of approved target paths before launching the job.
