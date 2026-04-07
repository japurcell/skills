## HIGH

### Arbitrary file read via path traversal in download endpoint

The change in `files.py:12` passes the user-controlled `name` parameter directly to `send_file()` as `DATA_DIR / requested_name` without normalizing or constraining it to `DATA_DIR`. An attacker can supply traversal sequences such as `../../etc/passwd`, or an absolute path such as `/etc/passwd`, and Flask will serve that file if the process can read it.

This is a high-severity local file inclusion issue because it exposes arbitrary server-readable files over HTTP, which can disclose credentials, application secrets, configuration, or other sensitive data.

Remediate by canonicalizing the requested path and enforcing that the resolved target remains under `DATA_DIR` before calling `send_file()`, or by limiting downloads to a vetted basename/allowlist.
