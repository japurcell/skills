# Vuln 1: Path traversal arbitrary file read: `files.py:12`

- Severity: HIGH
- Category: Path traversal
- Confidence: 0.98
- Description: The pending change removes the basename normalization and resolved-path boundary check before calling `send_file`, and now passes `DATA_DIR / requested_name` directly to Flask. Because `requested_name` comes from `request.args["name"]`, an attacker can supply traversal sequences such as `../../../../etc/passwd` or an absolute path to escape `/srv/reports` and read any file that the service account can access.
- Exploit Scenario: An unauthenticated attacker requests `/download?name=../../../../etc/passwd`. The handler constructs a path outside `DATA_DIR` and `send_file` serves the target file, disclosing sensitive host files or application secrets.
- Recommendation: Restore the previous containment logic before serving the file. Normalize the user input to a safe filename or resolve the candidate path and reject any request whose resolved path is not inside `DATA_DIR`. Keep the check in the request path closest to the file read.
