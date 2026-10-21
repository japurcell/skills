Check actual dispatch arguments against the route, runtime-limit monitoring, and runtime metadata. Distinguish **selected**, **submitted**, and **executed** settings. Worker reports cannot confirm execution; missing runtime evidence leaves executed settings **unconfirmed**.

1. **Dispatch omitted effort:** Noncompliant, even if runtime used the intended default. Cancel if supported and safe. Otherwise, disclose the mismatch before relying on results. Redispatch at most once with exact routed model and effort, when safe and useful. Do not treat dependent work as having a compliant prerequisite.

2. **Documented equivalent model alias:** Not a mismatch. Verify documented equivalence, matching effort, runtime monitoring, and remaining dispatch requirements. If those checks pass, dispatch remains compliant. Dependent work may proceed after output acceptance checks.

3. **Materially different executed configuration:** Report routing failure and pause affected dependent work, even if submitted settings matched the route. Preserve runtime evidence and diagnose the override. If capabilities changed, invalidate the route and reroute; do not silently substitute settings. Resume affected work only after resolving the failure and verifying prerequisite outputs.

Correct-looking output does not establish compliance.