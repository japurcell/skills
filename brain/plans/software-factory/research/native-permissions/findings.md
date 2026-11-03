# Native permission interaction design

> Policy update, 2026-10-15: the [observability-only amendment](../../tickets/human-control-and-publication.md#observability-only-amendment-2026-10-15) supersedes this report's dashboard-input recommendation. Native protocol findings remain evidence for command-side interaction; no CLI response transport is validated here. The adoption note below describes the earlier decision.

Research date: 2026-10-14. Subsequent decision: the human adopted the dashboard approval inbox and keeping the foreground runner alive during native permission waits. The [owning decision record](../../tickets/human-control-and-publication.md#accepted-dashboard-inbox-and-native-permission-waits) is authoritative; details below remain research recommendations unless adopted there. Three delegated research tickets and the human-control design ticket are closed. No factory adapter or authenticated permission round trip was implemented or tested.

## Recommendation

Use a **dashboard permission inbox backed by harness-specific protocol adapters**. The foreground runner owns native processes and permission exchanges; the independent dashboard renders saved requests and submits explicit responses through factory HTTP controls. Keep native policy enforcement and scopes intact. Do not depend on parsing terminal screens or attaching a human terminal to an already running JSON-output job.

This replaces the earlier unadopted recommendation to default to each harness's native interactive surface. Four harnesses expose plausible structured routes. Pi needs a clearly different capability declaration. A common user experience does not require identical native protocols or permission semantics.

## Findings by harness

| Harness and studied version | Recommended integration | Decisive constraint | Evidence |
| --- | --- | --- | --- |
| Codex 0.162.1 | Runner-owned `codex app-server --listen stdio://`; native request/response RPC | `exec --json` and its TypeScript SDK wrapper cannot answer human approval requests. Python SDK behavior differs and its defaults/reader callback are unsuitable for an assumed long-wait human bridge. | Local help/schema probes plus pinned source; [report](codex/findings.md), [official protocol](https://learn.chatgpt.com/docs/app-server). |
| Copilot CLI 1.0.97 + SDK 1.0.21 | SDK controlling the local CLI over stdio, with explicit permission events/responses | CLI permission flags and SDK policy handling are not equivalent. Reject profiles whose deny, managed, sandbox, or scope requirements cannot be preserved. ACP is another candidate, currently documented as preview. | Pinned SDK source and docs; local help/version probe failed during protected cache extraction. [Report](copilot-gemini/findings.md), [SDK compatibility](https://github.com/github/copilot-sdk/blob/f9a6c731432bec99b0a63a24cda1e77a29697634/docs/troubleshooting/compatibility.md). |
| Gemini CLI 0.64.0 | `gemini --acp`, implementing `session/request_permission` | Headless stream JSON cannot answer interactive asks. Respond using offered native option IDs; cancellation must settle pending permission requests. | Pinned source and docs; CLI absent locally. [Report](copilot-gemini/findings.md), [ACP implementation](https://github.com/google-gemini/gemini-cli/blob/4a0749aceac5643e6f85a36d7420314d85e13b52/packages/cli/src/acp/acpSession.ts#L707). |
| OpenCode V1 1.19.0 + matching SDK 1.19.0 | Managed `serve` child per active attempt, unique loopback port, HTTP permission replies and SSE events | Noninteractive JSON run auto-rejects asks. Remembered V1 grants are directory-instance state, potentially shared across sessions; prefer once and isolated server instances. Do not mix V1 with OpenCode V2 product contracts. | Pinned source and docs; CLI absent locally. [Report](opencode-pi/findings.md), [permission service](https://github.com/anomalyco/opencode/blob/v1.19.0/packages/opencode/src/permission/index.ts). |
| Pi 1.2.0 | RPC for sessions and extension UI; native tool approvals advertised unavailable | Project trust and generic confirmation dialogs are not a built-in tool approval gate. A required tool-approval capability needs an explicitly configured, tested enforcement extension or another compatible harness. | Pinned source and docs; CLI absent locally. [Report](opencode-pi/findings.md), [security contract](https://github.com/earendil-works/pi/blob/v1.2.0/packages/coding-agent/docs/security.md). |

The OpenCode SDK's `/v2` export is a generated client interface name, not the OpenCode V2 product. The report preserves this distinction and the source/docs disagreement about remembered-grant scope. These are researched version combinations, not permanent product pins or validated release support.

## Proposed interaction

```mermaid
sequenceDiagram
    participant H as Native harness
    participant R as Foreground runner and adapter
    participant S as Repository SQLite
    participant U as Independent dashboard
    H->>R: Permission request with native identity and options
    R->>S: Save request, attempt identity, scope and provenance
    S-->>U: Factory SSE after persistence
    U->>R: Explicit response through factory HTTP control
    R->>S: Validate current owner and request; record decision
    R->>H: Native protocol response
    H-->>R: Resolution and subsequent execution events
    R->>S: Record observed outcome or uncertainty
    S-->>U: Updated saved status
```

The diagram is logical routing, not a selected IPC or SQLite transaction implementation. The dashboard's HTTP service may persist a control command for the foreground owner; it never launches workflow work itself. Browsers do not talk directly to native server ports or receive their credentials. Local access authorization and owner fencing still need detailed specification in the control/recovery work.

Proposed adapter and UI obligations:

1. Record run, step, attempt, native session/turn/request, process generation, adapter version, relevant workspace/action and effective permission profile. Keep native payload provenance. A reused numeric request ID after process restart is a different request.
2. Show the requested operation and actual supported choices. Prefer one-action approval for new human choices; show the true scope of broader options explicitly. Never turn a generic Allow button into an implicit persistent rule or auto-approve handler. Existing configured permissions remain part of the effective profile.
3. Keep permission requests, user questions, MCP elicitation, project trust, OS setup/UAC, and factory checkpoints distinct. Each may have different cancellation, scope, or UI requirements. A native denial can let an agent try another approach; it is not necessarily Pause or Cancel.
4. Continue draining all native output while a response waits. Start with separately owned native processes per active agent attempt for isolation and interruption clarity. Existing repository-wide agent limits still apply; a live waiting session does not disappear from capacity accounting.
5. A saved response is not proof that the harness received it, executed the tool, or completed the action. Persist dispatch/resolution evidence separately. Duplicate controls cannot repeat an action; ambiguous response delivery requires reconciliation, not blind replay.
6. On unsupported required capabilities or policy mismatches, stop before dispatch with an explanation. Preserve the already accepted explicit fallback policy. Pi remains usable for profiles not requiring native tool approvals; lack of that capability does not silently authorize a new fallback or impose a mandatory factory sandbox.

## Two kinds of human wait

| Wait | What remains alive | Proposed exit and recovery behavior |
| --- | --- | --- |
| Factory checkpoint, such as approval of a final diff | Durable factory request, no native callback required | Preserve the accepted save-and-exit behavior when no active work or uncertain effects need supervision. Answers can be saved while stopped; explicit Continue starts execution. |
| Native tool permission during an agent attempt | Live native turn/callback or protocol request | Keep the foreground owner and native child alive while waiting. Closing the dashboard does not stop them. If the user pauses/cancels or the process dies, retire the live control and reconcile; a saved row cannot revive its callback. |

The human adopted this distinction after reviewing the research. The alternative was to interrupt native work whenever human input is needed and reconstruct it on Continue, adding repeated work without guaranteeing the identical request reappears. Keeping a workflow daemon alive merely to preserve callbacks would conflict with the selected foreground model.

Native pending requests are process-lifetime state in inspected Codex, Gemini and OpenCode paths; Pi extension UI uses a process-local map. Copilot persists some events, but its closed runtime's disconnect/pending-request outcome remains unproved. Accordingly, treat a disconnected owner as uncertain and its controls as unavailable until reconciliation. If the same surviving process can be positively recovered, an adapter may re-list/replay genuinely live requests; never infer liveness from historical events. After process replacement, require a fresh native request and fresh human response where native policy asks. Previously recorded approval is audit evidence, not a transferable grant.

Pause and Cancel retain their accepted thirty-second configurable grace and owned-process escalation. Before termination, use the native interruption mechanism and settle pending callbacks with the correct reject/cancel semantics where supported. Continue does not grant permissions, reset budgets, or erase uncertainty about earlier effects. Cancel cannot roll back a remote action already accepted.

## Packaging and platform fit

Keep adapters and SDK dependencies in the isolated, versioned factory installation. Pin the adapter, native binary/protocol and any permission extension together; retain compatible versions for unfinished runs. The skill can check binary identity, protocol capabilities and prerequisites without changing application dependencies. An upgrade must not substitute a different permission mode merely because the new executable starts successfully.

App-server and ACP stdio need no terminal interaction for their approval transport. OpenCode needs a runner-owned local HTTP child with port/access isolation. These are helper processes within an invocation, not a permanent factory service or external workflow engine. Pi requires no additional approval extension unless the chosen profile requires that capability.

All five have documented native platform paths, with differing shell/sandbox prerequisites. None of these reports proves end-to-end native Windows, Linux, or macOS lifecycle behavior. WSL is not native Windows evidence. OpenCode recommends WSL for some compatibility; Pi documents Git Bash; Copilot documents PowerShell prerequisites; Codex has platform-specific sandbox setup. Preserve those distinctions in support claims rather than claiming uniform parity from portable transport alone.

## Required proof before implementation support claims

The reports provide detailed per-harness acceptance cases. The shared conformance bar is:

- With two sessions, one waits for permission while the other streams and finishes; no crossed responses or unbounded output buffering.
- Prove one-action approval, denial, supported broader grants, effective managed/deny policy and required sandbox behavior. Tool effects must not precede required approval.
- Race duplicate/late responses against Pause, cancellation, child exit and process-ID reuse. Confirm request resolution separately from tool completion.
- Disconnect only the dashboard, then separately crash the foreground owner or native child. Continue must reconcile partial effects, preserve budgets and reject stale controls.
- Prove native Windows process-tree cleanup separately from Unix signals; record unsupported cases rather than bypassing controls.
- For Pi extensions, prove actual loading, coverage, failure behavior and cancellation. Generic dialog support alone does not pass the capability requirement.

No installation or authenticated model job was performed. Codex local schema/help probes succeeded; Copilot probes failed before command handling; other binaries were absent. Source fixtures were inspected, not executed. This supports the recommended architecture, with explicit implementation acceptance gates, rather than a claim that all adapters already work.

## Research records

- [Codex permission feasibility](../../tickets/codex-permission-feasibility.md)
- [Copilot and Gemini permission feasibility](../../tickets/copilot-gemini-permission-feasibility.md)
- [OpenCode and Pi permission feasibility](../../tickets/opencode-pi-permission-feasibility.md)
- [Delegation audit](delegation-audit.md)

The dashboard bridge and live-native-wait distinction are adopted. The human also selected one-action grants by default, with broader native grants exposed only when profiles permit those scopes. The [closed resolution](../../tickets/human-control-and-publication.md#resolution) owns the contract and future acceptance cases. Earlier accepted publication and control decisions remain unchanged.
