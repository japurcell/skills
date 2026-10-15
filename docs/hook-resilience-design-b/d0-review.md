# Independent D0 promotion review

Reviewed on 2026-10-15 by `/root/review_d0`, read-only. No tests or Git mutations were authorized for this review. The primary retains this result as a pending promotion gate, separate from successful component experiments.

## Current verdict: D0 feasibility promoted, production acceptance remains open

The frozen prototype (`d0-probe.py` fingerprint prefix `a68052fb`) skips tree occurrences at line 171 when the blob is absent from the acquired object set after remote-old subtraction. The filename rule runs only after this skip. Therefore safe bytes published under an ordinary path can be reused under a credential filename in an incremental push and evade the path rule. Source confidence: 95%. Required repair: reproduce an actual initial publication plus incremental same-blob credential-path publication, observe the false clean, apply path policy before the content-dedup skip, and prove actual rejection. Existing new-blob/new-ref controls do not cover this interaction. The original defect was repaired and independently reviewed. `path-control.json` proves actual incremental rejection with the remote unchanged; `failed-path-before.json` retains the original false allow.

## Production obligation and evidence limits

The prototype's remote-old graph verification uses ordinary captured subprocess output at lines 106-110, outside the protected-capture counters and enumeration timer. This was repaired: remote-old graph checks now use maintained protected capture/shared deadlines and contribute to capture/temp/enumeration accounting. Production retains its broader hostile-input and workload acceptance.

The reviewer traced transaction identity, private LFS handoff, upload ordering, cancellation and evidence limits. Real Git and real endpoint assertions are useful. All 13 final capacity fingerprints matched the inspected files. Earlier failed observations were preserved. Prototype RSS/materialized-content costs and unverified production/platform behavior were accurately qualified. These strengths do not override the path-policy blocker.

## Repair verification

Independent source re-review cleared the repair at probe SHA-256 `f711d37bbb898650d13a50af9763f808e69b754026a0156cb7d7c881427b9e10` with no new blockers. It also confirmed the12-ref late control includes all original histories. At that review read, the capacity artifact had not yet been replaced, so the reviewer explicitly withheld capacity approval. After replacement, the primary verified all13 current fingerprints, all9 distinct workloads/paired outcomes, every paired logical volume at least the clean workload, and one exact67,108,864-byte LFS delivery. Multi-ref logical bytes: clean12,585,828; paired12,586,097. This satisfies the independent review's remaining deterministic condition. Integrated D0 commit: `555aa6bf8ff49f77a3979730744d1621543586b5`. No production installation or platform approval follows from this laboratory result.
