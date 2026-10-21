**Router return value**

Router returns final routing decision (never tentative or approval request) in this YAML schema:

```yaml
dispatchable: true
tier: <Fast|Standard|Premium>
model: <exact dispatch value>
reasoning_effort: <exact dispatch value>
reason: <task fit, capability floor, cost assumptions, and uncertainty>
escalation_trigger: <concrete trigger or none>
fallback:
  model: <exact same-tier dispatch value>
  reasoning_effort: <exact dispatch value>
```

`fallback` is `none` only when no other exact same-tier configuration satisfies runtime capabilities and user constraints; `reason` then explains what excluded alternatives. For availability-driven promotion, `tier` reports the selected configuration's tier and `reason` states the lower floor plus the availability increase.

**Storage and presentation control**

Router defines the required output contract and fields. Caller or host controls downstream storage, persistence, and user presentation, and must explicitly apply the returned `model` and `reasoning_effort` when delegating without requesting separate model-selection permission.

**Implicit model or effort values**

No. Separation between routing, storage, and presentation never permits implicit, inherited, conditional, ranged, or unresolved values (`default`, `auto`, `runtime-selected`, `runtime default`, `"runtime-supported"`, `"high or greater"`, `"strongest available"`, `"if applicable"`, or unexpanded placeholders). Both `model` and `reasoning_effort` (and any `fallback`) must remain exact values accepted by the dispatch interface, or the route is `dispatchable: false` and cannot be dispatched.
