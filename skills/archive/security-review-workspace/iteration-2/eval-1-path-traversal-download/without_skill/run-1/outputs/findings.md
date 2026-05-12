# Vuln 1: Path traversal arbitrary file read in `files.py:11`

- Severity: HIGH
- Category: Path Traversal
- Confidence: 0.98
- File: `files.py:11`
- Description: The new implementation passes a user-controlled `name` parameter directly into `send_file(DATA_DIR / requested_name)` without normalizing the path or constraining it to `DATA_DIR`. The previous code stripped path components with `Path(requested_name).name`, resolved the candidate path, and rejected anything outside `/srv/reports`; that protection has been removed. An attacker can now supply traversal sequences such as `../../../../etc/passwd` and cause Flask to read and return files outside the intended reports directory.
- Exploit Scenario: A remote caller requests `/download?name=../../../../etc/passwd` or another sensitive server path. Because the handler joins and serves that path without confinement checks, the application returns arbitrary readable files from the host filesystem, exposing credentials, configuration, or other sensitive data.
- Recommendation: Restore confinement before calling `send_file`. Normalize to a basename if nested paths are not required, or resolve the joined path and verify it remains under `DATA_DIR.resolve()` before serving it. Reject traversal attempts with `403` or `404`.
