# E1. Exercise externally observable orchestration decisions

Owner: controlled-eval implementer. Prerequisite: evidence boundary in Decision Log. Inputs: verified historical five-minute prompt/SELECT case, existing scheduler tests and ExecPlan authoring evals. Own scripts/tests/orchestration/ controlled fixtures, grader and test instructions. Start with an observed read-only prompt in the trace or an equivalent five-minute negative control. Use small synthetic workloads, no private trace data in Git.

Grade quiet waiting without extra dispatch/setup, two-worker early completion moving the deadline, silent expiry, exactly one extension and a bounded response deadline, and shutdown before transfer (old worker still running or only its writes active). Exercise same-worker acknowledgement using a known setup fact and the replacement path with environment, pinned revision and evidence. Compare two reports for owner, revision, evidence, blocker, deadline and next action without repeated setup. Grade actual observable actions and work results; source labels, prefilled pass flags and keyword counts alone cannot prove these outcomes. Include deliberate failures, missing evidence, and a legitimate deadline action accepted by the same grader. Document input format and run `rtk proxy python3 -m unittest discover -s scripts/tests/orchestration`. Stop when controlled evidence has an auditable verdict independent of native availability.
# Controlled orchestration evidence

The fixture suite lives under `scripts/tests/orchestration/`. It drives the
public scheduler CLI with temporary state and small child processes. It covers
the five-minute quiet lookup before a ten-minute deadline, a genuine emitted
deadline event, two assignments where early completion leaves the later
deadline next, status expiry and one ETA-based extension, and transfer gating
against live worker and writer subprocesses. Continuity uses a same-process
known-fact follow-up and a replacement process receiving environment, pinned
revision, and evidence. Two report objects are checked against the six-field
contract, with negative mutations for missing evidence, false transfer while
processes remain, failed handoff, missing report data, and repeated setup.

Run `rtk proxy python3 -m unittest discover -s scripts/tests/orchestration`.
The grader consumes observed state, CLI events, child replies, and process
liveness; it does not consume a fixture pass label. CLI shutdown confirmation
remains an explicit host assertion and does not prove host-side quiescence.
These controls do not establish native dispatch, notification, agent memory,
cancellation, or write shutdown behavior; those need live-host evidence.
