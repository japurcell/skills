# T4c, delivery

After T4a and T4b, wire the proven host-specific wait into `skills/default/delegate-to-subagents/SKILL.md` and `skills/default/execplan-implement/SKILL.md`. Use a wait for any completion with a bounded deadline, or an independent completion notification with a single timer. When neither is available, document the measured latency. Repeat the matched workload on the candidate. Prompt delivery requires QUICK consumption before SILENT's earlier deadline and evidence that the parent still services SILENT on expiry. Stop after recording the result for each claimed host/caller combination.

The host-workflow implementer owns the callers, native trial records and combined proof. Use T4a's observed capabilities or explicit limitations, and T4b's actual interface. Preserve prompt delivery only on host paths that demonstrate it. Record native trial status per caller.

Use the [milestone contract and verification commands](4-scheduler-wake.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Local result

On 2026-11-19, based on `ee7f986f`, both callers describe completion-first handling and wake refresh. The delegate uses T4b's locked `next-wake` result (`wake`: null or `assignment`, `agent`, `due`, `reason`); ExecPlan retains its independent registry and includes reservations before handle attachment. The recipe now specifies positive and inverted arms and the evidence required for each.

Local checks: scheduler CLI 21 tests, historical W1 12 tests, and controlled orchestration 11 tests passed. The added controlled inverse case simulates QUICK observation and admission at 6 before SILENT's deadline at 10, re-arms SILENT and observes its expiry and checkpoint wake at 15. It does not exercise a native parent or establish native delivery latency. Frozen W1 arms were unchanged.

No authenticated native calls were made. T4a's baseline was blocked before launch and neither caller has a native candidate trace. Prompt delivery remains unverified for both Codex and Copilot paths; compare both arms for each caller in an authorized host session before claiming it. The local fixture is not a substitute.

Guidance review traced empty and overdue wakes, unattached reservations, completion-before-expiry and a single-worker wait. No additional material issue remains in the edited instructions. Reflection found no durable knowledge requiring a brain or skill change.
