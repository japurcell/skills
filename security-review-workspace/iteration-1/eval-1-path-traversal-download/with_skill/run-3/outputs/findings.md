# Vuln 1: Path traversal arbitrary file download: `files.py:12`

- Severity: HIGH
- Category: Path Traversal
- Confidence: 0.98
- Description: The `/download` handler now passes `DATA_DIR / requested_name` directly to `send_file()` with no normalization or containment check. Because `requested_name` comes from `request.args["name"]`, an attacker can supply traversal sequences such as `../../etc/passwd` and escape `/srv/reports`, causing the server to return arbitrary readable files from the filesystem.
- Exploit Scenario: An unauthenticated attacker requests `/download?name=../../etc/passwd` or another sensitive path. Flask serves the resolved file from outside the reports directory, exposing system files, application secrets, credentials, or other tenant data.
- Recommendation: Restore the previous containment guard by reducing user input to a basename or by resolving the candidate path and rejecting any request whose resolved path does not remain under `DATA_DIR`. Prefer an allowlist of report identifiers over direct file path input.
