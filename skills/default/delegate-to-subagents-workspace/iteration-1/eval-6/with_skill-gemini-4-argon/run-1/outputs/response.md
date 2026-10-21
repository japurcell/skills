### Verification checks

Inspect actual dispatch arguments and runtime-control state. Compare submitted `model` and `reasoning_effort` against the router decision, verify explicit submission of both outside the worker prompt, and check runtime-limit monitoring. Distinguish selected, submitted, and executed settings: only runtime metadata confirms executed values (otherwise mark `unconfirmed`; never trust worker self-reports).

### Case 1: Dispatch omitted `reasoning_effort`

- **Compliance**: Noncompliant. Both exact `model` and `reasoning_effort` must be explicitly submitted; omitted, null, inherited, or runtime-selected values do not qualify. Never describe this dispatch as router-selected, and correct-looking output does not establish compliance.
- **Recovery**: Cancel the dispatch if supported and safe; otherwise disclose the mismatch before relying on results. Redispatch at most once with both exact routed values explicitly submitted when safe and useful.
- **Dependent work**: Hold dependent work until the compliant redispatch completes and is verified, or until the mismatch is disclosed before relying on its results.

### Case 2: Runtime metadata reports a documented equivalent model alias

- **Compliance**: Compliant. Runtime metadata confirms executed values, and documented alias resolution is not a mismatch.
- **Recovery**: None needed. Record executed setting as confirmed via runtime metadata.
- **Dependent work**: Proceed normally once the subtask output passes acceptance verification.

### Case 3: Runtime metadata reports a materially different executed configuration

- **Compliance**: Routing failure / material execution override (confirmed by runtime metadata).
- **Recovery**: Report the routing failure briefly to the user. If the routed configuration is unavailable in runtime capabilities, exclude it and reroute through `subagent-model-router` for a complete replacement without lowering the capability floor.
- **Dependent work**: Pause all affected dependent work immediately.