# ExecPlan Integration

**Type:** grilling
**Status:** closed
**Blocked By:** rtk-setup-warning.md, markdown-health-hook.md, security-hook-notifications.md, repository-state-guardrails.md, scan-secrets-shutdown.md, read-only-orientation.md, powershell-authoring-guidance.md, disposable-probe-files.md
**Research Dir:** none

## Question

How should the eight resolved outcomes be ordered into one self-contained ExecPlan, with independently verifiable milestones, shared test coverage, platform-specific acceptance, safe installation checks, and disposition of the Ready entries in `docs/ideas.md`?

---

## Resolution

The [integrated ExecPlan](../ExecPlan.md) orders the eight resolved Ready problems as separate, verifiable implementation milestones: Read Only Orientation, PowerShell Authoring Guidance, Disposable Probe Files, Scan Secrets Shutdown, Security Hook Notifications, Repository State Guardrails, Markdown Health Hook, and RTK Setup Warning. Shared provider hook transport precedes hook-dependent milestones; final integration and documentation form a separate last milestone. Codex receives a baseline scan-secrets adapter during shared setup so Scan Secrets Shutdown can be accepted across all three providers before security banner work.

Each milestone names source and test locations, user-visible behavior, failure handling, and acceptance evidence. Source and temporary-home checks precede installed local smoke. Native Windows automation and a supplemental live-check procedure cover applicable Windows behavior; a live Windows run is not the completion gate. Disposable Probe Files keeps the user's later, narrower three-instruction-file scope without installer, local-agent, or Windows checks. [Ideas](../../ideas.md) now links to the ExecPlan under `Planned` rather than repeating the eight Ready entries. This ticket delivers the plan, not feature implementation.
