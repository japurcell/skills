Exact router values alone do not establish compliance. Check actual dispatch arguments and runtime metadata separately.

| Case | Compliance | Recovery and dependent work |
|---|---|---|
| Actual dispatch omitted effort | **Noncompliant**, even if runtime happened to choose the routed effort. | Cancel if supported and safe. Otherwise disclose mismatch before relying on results. Redispatch at most once with explicit routed values when safe and useful. Hold dependent work requiring that result until corrected or explicitly assessed after disclosure. |
| Runtime reports a documented equivalent model alias | **Compliant**, assuming submitted model and effort matched the recorded route and all other gates passed. | Record confirmed alias as equivalent canonicalization. No reroute or replacement needed. Dependent work proceeds after prerequisite output verification. |
| Runtime reports materially different executed configuration | **Routing failure**, despite correctly submitted arguments. | Report override and pause affected dependent work. Investigate runtime controls; reroute if capabilities changed. Record revised route before any redispatch. Do not treat overridden execution as compliant fulfillment. |

Check explicit runtime-limit enforcement and any required approval too. Distinguish **selected**, **submitted**, and **executed** values. Unreported execution values remain `unconfirmed`; agent self-report is not runtime confirmation.

These are checks only. No dispatch or file writes performed.