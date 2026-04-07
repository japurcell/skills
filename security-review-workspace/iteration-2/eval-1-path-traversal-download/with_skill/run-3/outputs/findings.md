# Vuln 1: Path traversal in download route: `files.py:12`

- Severity: HIGH
- Category: Path traversal
- Description: The pending diff removes the previous `Path(requested_name).name` and `resolve()` boundary check, then passes `DATA_DIR / requested_name` directly into `send_file()`. An attacker can supply values like `../../etc/passwd`, causing the server to read and return files outside `/srv/reports`, which turns this endpoint into an arbitrary file read primitive.
- Recommendation: Restore canonicalization and containment checks before calling `send_file()`, for example by resolving the candidate path under `DATA_DIR` and rejecting requests whose resolved path escapes that directory.
