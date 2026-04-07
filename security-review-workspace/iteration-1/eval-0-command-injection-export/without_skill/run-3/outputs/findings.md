## HIGH: Command injection via user-controlled shell command

- Location: /home/adam/.agents/skills/security-review/evals/files/command-injection-export/app.py:13-15
- The pending change replaces the safe argv-style subprocess invocation with a formatted command string and sets `shell=True`. The `target` value comes directly from `request.json["target"]`, so an authenticated caller can supply shell metacharacters such as `;`, `&&`, or `$(...)` and execute arbitrary commands on the server.
- Impact: any caller with a valid `X-Ops-Token` can turn the archive endpoint into remote code execution as the service account, which can lead to data theft, destructive actions, or lateral movement.
- Recommendation: call `subprocess.run` with a list of arguments and keep `shell=False`. If the service must accept only approved filesystem targets, validate `target` against a strict allowlist of expected paths before invoking the subprocess.
