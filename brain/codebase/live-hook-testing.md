# Live provider checks

- Use isolated provider profiles or temporary projects. Repository task authorization does not imply modifying global installations.
- Record a nonce, provider version, event entry, process completion, and user-visible output/context independently.
- Prepare and clean up probes through `scripts/probe-provider-hook-delivery.py`; preserve unrelated settings and handlers.
- Keep probe logs outside disposable Git trees; exclude logs/audits from secret-scanning candidates.
- Verify timeouts as well as normal delivery. CLI progress output is not interchangeable with VS Code visibility.
- Require a real deployed Gemini `AfterAgent` probe before claiming enforcement. Source/config checks do not prove it.

Evidence: [probe CLI](../../scripts/probe-provider-hook-delivery.py), checked 2026-10-20. Historical provider passes do not establish current installation behavior; recheck after CLI/hook changes.
