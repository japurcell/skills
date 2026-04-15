# Vuln 1: Arbitrary file read via path traversal: `files.py:12`

- Severity: HIGH
- Category: Path traversal
- Description: The pending change removes the basename-and-resolve containment check and now passes `DATA_DIR / requested_name` directly to `send_file`. An attacker can supply values like `../../etc/passwd` in the `name` query parameter, causing Flask to read and return files outside `/srv/reports` that are readable by the process.
- Recommendation: Restore canonicalization and an allow-within-`DATA_DIR` check before calling `send_file`, or switch to a safe helper such as `send_from_directory` that rejects traversal sequences.
