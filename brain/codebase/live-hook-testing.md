# Live provider checks

- Use the smallest supported behavior boundary with disposable projects/state. Verify whether a private profile hides an existing provider-owned login before imposing it. Repository task authorization does not imply modifying global installations.
- Record a nonce, provider version, event entry, process completion, and user-visible output/context independently.
- Prepare and clean up probes through `scripts/probe-provider-hook-delivery.py`; preserve unrelated settings and handlers.
- For probe CLI contract changes run [the probe regression suite](../../scripts/tests/hooks/test-probe-provider-hook-delivery.py).
- Keep probe logs outside disposable Git trees; exclude logs/audits from secret-scanning candidates.
- Verify timeouts as well as normal delivery. CLI progress output is not interchangeable with VS Code visibility.
- Measure provider startup-to-handler-entry latency separately from handler completion time. Fast handler runtime alone cannot prove a one-second provider deadline; exercise the actual timeout before claiming compliance.
- Require a real deployed Gemini `AfterAgent` probe before claiming enforcement. Source/config checks do not prove it.

## Native authentication and adapter boundaries

- Environment-token absence proves only process environment state. Compare provider-native authentication/status in the intended runner environment; keep credential lookup provider-owned and retain only safe status fields.
- Freeze safe behavior/configuration and component inventories instead of hashing whole credential-bearing user configuration. The scheduler pilot encodes this boundary in [provider context and native metadata checks](../../skills/default/delegate-to-subagents/evals/scheduler_pilot.py), with [public CLI regressions](../../skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py).
- Before declaring native evidence unsupported, inspect exact retained successful task execution and its version-pinned metadata. Compare transport item identities, logical commands and session/turn context without treating display IDs or requested settings as executing proof.
- Integrate and probe the installed CLI at small no-inference boundary checkpoints before extending a large adapter. Ground asynchronous notification fixtures in documented schemas and observed sanitized envelopes. An unknown notification failure can reveal a fixture coverage gap while strict rejection remains the correct current behavior.

## Probe troubleshooting

- For a Gemini latency probe requiring `GOOGLE_CLOUD_PROJECT`, set it in the same child process that launches the CLI; record the propagation check without recording its value.
- An empty Gemini override log does not prove absent dispatch. Inspect the default installed log, then invoke the emitter directly with the override to distinguish dispatch, environment propagation, and emitter failure.
- If macOS `xcrun` fails because its sandbox cache is unavailable, a safe-read probe may use a verified native Git binary with `--no-optional-locks`. Record the environment failure and the binary used; do not generalize this workaround to other operations.

Evidence: [probe CLI](../../scripts/probe-provider-hook-delivery.py), checked 2026-10-20. Historical provider passes do not establish current installation behavior; recheck after CLI/hook changes.

Compare the complete safe native response shape before sanitizing fixtures. Omitted fields in a projection can create a false platform limitation. Inventory inherited components after applying the intended disabling controls, and normalize omitted false fields only when native serialization proves that default. Native smoke coverage must exercise required output authoring as well as command execution. Maintain full real-child scenario fixtures alongside the focused transport checks. The scheduler [adapter](../../skills/default/delegate-to-subagents/evals/scheduler_pilot.py) and [fixtures](../../skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py) encode these boundaries.
