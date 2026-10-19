# SSSF approvals and lifecycle comparison

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/sssf-lifecycle-comparison/

## Question

At the previously studied SSSF commit, how do human questions/approvals, live UI reliability, interruption, and installation actually work? Distinguish human-labelled trace phases from interactive requests, headless agent questions from permission approvals, and source behavior from documentation claims. Compare against our current planning scope without changing product decisions. Retain primary-source links and evidence limits.

## Resolution

Pinned-source findings are recorded in [findings.md](../research/sssf-lifecycle-comparison/findings.md). In this snapshot, the supplied workflow has no human approval or input wait: its engineer phase records the CLI request, while the selected headless Pi adapter sends prompts through argv, disables stdin, and treats a prose question as invalid structured output. The visualizer polls SQLite every 500 ms and retries failed requests without backoff; partial pagination failure can advance the mounted view's cursor before fetched events are appended. SIGTERM/SIGINT mark the run failed and close process rows but do not terminate the Pi child; no agent timeout or SIGKILL cleanup path was found. Installation copies stamped files but does not provision prerequisites or record an SSSF version; `--force` overwrites stamped edits, and no uninstall contract is documented.

These are source-based findings at commit `de31374882e7a4e3e5b7bb9bd09e69dc2f779356`, not runtime-tested behavior. The findings document links each claim to the pinned primary source and records limits and documentation/source discrepancies. Existing planning decisions remain unchanged.
