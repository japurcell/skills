**1. Actual dispatch omitted effort**
- **Compliance:** `routing_compliant: false`. `submitted.reasoning_effort` missing; does not match `route.reasoning_effort`.
- **Recovery:** Do not describe as router-selected. Cancel if supported and safe; otherwise disclose mismatch before using result. Redispatch at most once with exact recorded `model` and `reasoning_effort` if safe and useful.
- **Dependent work:** Block until compliant replacement completes and verifies, or until mismatch is disclosed before relying on the result.

**2. Runtime reports documented equivalent model alias**
- **Compliance:** `routing_compliant: true`. `submitted` matched `selected`; `executed` differs only by documented alias/canonicalization, not material override.
- **Recovery:** Record the alias in `executed.model` in the session artifact. No cancellation or redispatch needed.
- **Dependent work:** Proceed once prerequisites and outputs are verified.

**3. Runtime reports materially different executed configuration**
- **Compliance:** Treat as material override and routing failure (`routing_compliant: false`).
- **Recovery:** Record `selected`, `submitted`, and actual `executed` values in the session artifact, and report the routing failure in chat. If capability availability changed, begin a fresh routing attempt with updated runtime capabilities.
- **Dependent work:** Pause all affected dependent work immediately.