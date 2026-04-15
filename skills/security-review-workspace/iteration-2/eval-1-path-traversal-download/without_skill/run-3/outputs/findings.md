# Vuln 1: Path traversal allows arbitrary file download in `files.py:12`

- File: `/home/adam/.agents/skills/security-review/evals/files/path-traversal-download/files.py`
- Line: 12
- Severity: HIGH
- Category: Path Traversal / Data Exposure
- Confidence: 0.98
- Description: The updated `/download` handler now passes `DATA_DIR / requested_name` directly to `send_file()` with no normalization or containment check. Because `requested_name` comes straight from the `name` query parameter, an attacker can supply traversal segments such as `../../etc/passwd` and escape `/srv/reports`, causing the server to return any file the process can read.
- Exploit Scenario: An attacker sends `GET /download?name=../../etc/passwd`. The joined path becomes `/srv/reports/../../etc/passwd`, which resolves to `/etc/passwd` when opened. If the application process can read that file, the endpoint will disclose it to the attacker. The same primitive can expose application secrets, configuration files, SSH keys, or other sensitive local data.
- Recommendation: Restore a strict containment check before calling `send_file()`. The previous pattern of resolving the candidate path and verifying it stays under `DATA_DIR` is acceptable, or use Flask/Werkzeug helpers such as `send_from_directory()` / `safe_join()` to constrain access to files within the intended directory.
