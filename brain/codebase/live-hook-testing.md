# Live provider checks

- Use isolated provider profiles or temporary projects. Repository task authorization does not imply modifying global installations.
- Record a nonce, provider version, event entry, process completion, and user-visible output/context independently.
- Prepare and clean up probes through `scripts/probe-provider-hook-delivery.py`; preserve unrelated settings and handlers.
- For probe CLI contract changes run [the probe regression suite](../../scripts/test-probe-provider-hook-delivery.py).
- Keep probe logs outside disposable Git trees; exclude logs/audits from secret-scanning candidates.
- Verify timeouts as well as normal delivery. CLI progress output is not interchangeable with VS Code visibility.
- Measure provider startup-to-handler-entry latency separately from handler completion time. Fast handler runtime alone cannot prove a one-second provider deadline; exercise the actual timeout before claiming compliance.
- Require a real deployed Gemini `AfterAgent` probe before claiming enforcement. Source/config checks do not prove it.

## Probe troubleshooting

- For a Gemini latency probe requiring `GOOGLE_CLOUD_PROJECT`, set it in the same child process that launches the CLI; record the propagation check without recording its value.
- An empty Gemini override log does not prove absent dispatch. Inspect the default installed log, then invoke the emitter directly with the override to distinguish dispatch, environment propagation, and emitter failure.
- If macOS `xcrun` fails because its sandbox cache is unavailable, a safe-read probe may use a verified native Git binary with `--no-optional-locks`. Record the environment failure and the binary used; do not generalize this workaround to other operations.

Evidence: [probe CLI](../../scripts/probe-provider-hook-delivery.py), checked 2026-10-20. Historical provider passes do not establish current installation behavior; recheck after CLI/hook changes.
