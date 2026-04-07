# Vuln 1: Path traversal arbitrary file read: `files.py:12`

- Severity: HIGH
- Category: Path traversal
- Confidence: 0.98
- Description: The pending change removes the previous `Path(requested_name).name` normalization and `resolve()`/prefix check, then passes the user-controlled `name` parameter directly into `send_file(DATA_DIR / requested_name)`. Because `requested_name` may contain traversal segments such as `../../../etc/passwd`, the resulting path can escape `/srv/reports` and cause the server to return arbitrary readable files from the host filesystem.
- Exploit Scenario: An attacker sends `GET /download?name=../../../etc/passwd` or a similar traversal payload. Flask resolves the combined path when opening the file, so the endpoint serves a file outside the intended reports directory, exposing sensitive local files, secrets, or application configuration.
- Recommendation: Restore confinement to the reports directory before calling `send_file`. A minimal fix is to normalize to a basename or canonicalize with `candidate = (DATA_DIR / requested_name).resolve()` and reject any path whose resolved location is not within `DATA_DIR.resolve()`. Prefer `candidate.relative_to(DATA_DIR.resolve())` or an equivalent safe-path check instead of string-prefix comparisons alone.
