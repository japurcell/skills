# Vuln 1: Path traversal enables arbitrary file download: `files.py:12`

- Severity: HIGH
- Category: Path traversal
- Description: The pending change removes the previous `Path(requested_name).name` and `resolve()` containment check, and now passes `DATA_DIR / requested_name` directly to `send_file()`. An attacker can supply traversal sequences such as `../../etc/passwd`, which the filesystem will resolve outside `/srv/reports`, turning the `/download` endpoint into an arbitrary file-read primitive over HTTP.
- Recommendation: Restore canonicalization and containment enforcement before calling `send_file()`, for example by reducing the user input to a basename or resolving the joined path and rejecting any target that escapes `DATA_DIR`.
