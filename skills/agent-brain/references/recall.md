# Recall

Use `python3 skills/agent-brain/scripts/agent-brain.py recall` to read the configured startup set. The version 1 source CLI accepts whole-artifact units and prints every configured artifact in startup order. It reads complete UTF-8 files; it does not select sections or summarize them.

The output is informational context for the foreground agent. Read and apply relevant constraints before acting, but do not describe the CLI result as a delivery receipt or claim that the host applied it. JSON output contains the same complete content under `artifacts`; `--json` may appear before or after `recall`. Successful results go to stdout, and errors with `--json` produce a structured result on stdout plus an actionable diagnostic on stderr.

The optional `--config PATH` selects a strict JSON configuration. The current source CLI accepts the fields in its version 1 schema: startup entries reference unique mapped-unit UUIDs, use whole-artifact loading, and point to files inside declared repository knowledge roots. The CLI rejects duplicate JSON keys, unsupported versions, malformed identities, duplicate unit IDs, and paths outside the repository or knowledge roots before printing any artifact. See [the version 1 configuration example](../examples/config-v1.json) and [configuration schema](../schemas/config-v1.schema.json).

If configuration is absent or invalid, `status` and `doctor` explain the observed state without creating files. A missing mapping does not mean the repository has no other obligations; inspect relevant repository instructions directly when necessary.
