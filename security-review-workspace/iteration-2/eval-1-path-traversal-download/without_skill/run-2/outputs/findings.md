# Vuln 1: Path Traversal Arbitrary File Read (`files.py:12`)

- File: `files.py`
- Line: `12`
- Severity: HIGH
- Category: Path Traversal
- Confidence: 0.98
- Description: The pending change now passes the raw `name` query parameter directly into `send_file(DATA_DIR / requested_name)` without canonicalizing the path or enforcing that the resolved file stays under `/srv/reports`. An attacker can supply traversal sequences such as `../../../../etc/passwd` to escape `DATA_DIR` and read any file the Flask process can access.
- Exploit Scenario: A remote user requests `/download?name=../../../../etc/passwd`. The handler joins that value onto `/srv/reports` and `send_file` serves the resulting path, allowing arbitrary local file disclosure. In a real deployment this can expose credentials, application secrets, SSH keys, or other sensitive system files.
- Recommendation: Restore path confinement before calling `send_file`. Resolve the candidate path and reject it unless it remains inside `DATA_DIR`, or reduce input to a basename if only flat filenames are supported. For example, compute a resolved candidate and verify it is relative to `DATA_DIR.resolve()` before serving it.
