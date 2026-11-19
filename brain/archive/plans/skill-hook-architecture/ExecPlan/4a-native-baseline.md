# T4a, baseline only

The native operator runs the currently shipped caller on a disposable project using the two-worker workload below. First record the positive control, then invert the actual registered deadlines so SILENT is due first while QUICK finishes first. Keep both assignments alive long enough to observe overlap. Capture registration, native completion, parent consumption, deadline action and terminal state. Stop after recording the old caller's results or the precise missing host capability.

The native operator owns the baseline evidence. Use disposable projects and provider-owned authentication. Capture the existing public matched workload, inverse ordering and consumption times or exact setup failure using scripts/tests/orchestration/native-lifecycle.md. Stop before candidate trials.

Use the [milestone contract and verification commands](4-scheduler-wake.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Local baseline, 2026-11-19

On macOS arm64, Codex CLI 0.170.0 reported an active ChatGPT login and Copilot CLI reported 1.0.114. The coordinator prepared separate synthetic positive and inverse projects. Automatic approval review blocked the authenticated Codex positive control before launch because its prompt and events could be transmitted to the provider. The user selected local checks. No workers ran in either arm and there are no native completion or consumption timestamps for either provider.

At the plan base, `rtk proxy python3 -B scripts/tests/orchestration/test_controlled.py` passed all nine offline tests. The scheduler implementer may use this as the fixture baseline. A future authenticated native trial still needs a provider-specific authorized session and the two actual registration/consumption traces.

## Authorized native trials, 2026-11-19

The user subsequently authorized synthetic authenticated trials with local-only transcripts. In the Codex 0.170.0 delegate positive control at `069b3f22`, SILENT was due at Unix 1795079241.337 and QUICK at 1795079220.271. The parent consumed QUICK at 1795079216.950, after its marker at 1795079207.372. SILENT's expiry was processed at 1795079251.681, followed by a checkpoint, extension and interruption at extension expiry. Its marker appeared after expiry; interrupted worker status and an unchanged marker were observed, but independent descendant process shutdown was not established. This control used 70/35-second deadlines and 150-second SILENT work; do not compare its timing as a matched arm against later 180/100-second deadline, 240-second work trials.

In the matched longer-margin Codex delegate inverse baseline, SILENT's deadline was 1795079576.890 and QUICK's was 1795079668.407. The parent consumed QUICK's native final at 1795079527.431, before SILENT's deadline; the marker was written at 1795079509.770. SILENT entered checkpoint and received its one extension; after the extension expired the parent interrupted it and recorded no marker, interrupted native status and no matching project sleep or marker writer in a process check. The candidate inverse is recorded in [T4c](4c-delivery.md). Both workers overlapped; observed final consumption times are upper bounds, not host-provided completion timestamps.

In the corrected standalone Copilot ExecPlan inverse baseline, QUICK's native completion event occurred at 09:29:31.832 UTC. The parent waited on SILENT from 09:29:49.120 to 09:30:52.204, when it began reading QUICK, at least 80.372 seconds after completion and after SILENT's re-anchored 09:30:49.465 deadline. It requested SILENT status at 09:31:51.577 and issued a local launcher kill at 09:32:09.440. The parent process timed out at 420 seconds; the operator independently confirmed the tracked launcher PID 6086 had exited. This establishes an observed single-worker wait delay, not a universal bound. The standalone positive baseline also timed out, although both native workers had completed; its lifecycle record was incomplete.

The Copilot delegate positive baseline registered SILENT due 1795080011.583 and QUICK due 1795079943.988. The parent consumed QUICK at 1795079873.466, ticked SILENT at 1795080011.584 and sent a stop request after checkpoint expiry. SILENT nevertheless wrote at 1795080081.741 and completed; no successful stop confirmation was recorded. Its inverse baseline fell back to nonoverlapping local commands and timed out, so no matched inverse baseline pass is claimed.

Process exit alone is not acceptance. Copilot attempts denied by noninteractive command permissions are setup failures, not timing results. Transcripts remain under private disposable directories, outside the repository.
