## HIGH: Download endpoint allows path traversal outside the reports directory

- Location: `files.py:11-12`
- The change removed both the basename restriction and the post-resolution boundary check, and now passes `DATA_DIR / requested_name` directly into `send_file`. An attacker can request values like `../../../../etc/passwd`, causing the application to read and return files outside `/srv/reports`.
- This is an arbitrary file read primitive. In practice it can expose application secrets, credentials, configuration files, and other sensitive host data reachable by the service account.
- Restore canonicalization and directory-boundary enforcement before serving the file, or use Flask/Werkzeug helpers designed for this pattern such as `send_from_directory` with strict validation.
