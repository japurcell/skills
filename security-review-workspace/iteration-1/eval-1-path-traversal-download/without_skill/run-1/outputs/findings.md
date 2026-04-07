## HIGH: Arbitrary file download via user-controlled path

- Location: `/home/adam/.agents/skills/security-review/evals/files/path-traversal-download/files.py:12`
- The new implementation passes `requested_name` directly into `send_file(DATA_DIR / requested_name)` without resolving the path or enforcing that it remains under `DATA_DIR`.
- This reintroduces path traversal and absolute-path access. Inputs such as `name=../../../../etc/passwd` or `name=/etc/passwd` can escape `/srv/reports` and expose any file readable by the application process.
- The removed code explicitly normalized the input to a basename, resolved the candidate path, and rejected requests outside the reports directory. Dropping those checks turns the download endpoint into an arbitrary file read primitive.
- Restore canonicalization and directory-containment validation before calling `send_file`, or restrict downloads to an allowlisted set of report names.
