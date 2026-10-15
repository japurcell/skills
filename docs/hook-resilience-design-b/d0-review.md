# Independent D0 promotion review

Reviewed on 2026-10-15 by `/root/review_d0`, read-only. No tests or Git mutations were authorized for this review. The primary retains this result as a pending promotion gate, separate from successful component experiments.

## Current verdict: changes required

The frozen prototype (`d0-probe.py` fingerprint prefix `a68052fb`) skips tree occurrences at line 171 when the blob is absent from the acquired object set after remote-old subtraction. The filename rule runs only after this skip. Therefore safe bytes published under an ordinary path can be reused under a credential filename in an incremental push and evade the path rule. Source confidence: 95%. Required repair: reproduce an actual initial publication plus incremental same-blob credential-path publication, observe the false clean, apply path policy before the content-dedup skip, and prove actual rejection. Existing new-blob/new-ref controls do not cover this interaction. D0 promotion remains unmet until repaired and reviewed.

## Production obligation and evidence limits

The prototype's remote-old graph verification uses ordinary captured subprocess output at lines 106-110, outside the protected-capture counters and enumeration timer. First-publication capacity evidence does not establish an incremental baseline traversal envelope. Bounded baseline acquisition/accounting must be demonstrated before claiming production acceptance; retain the limitation explicitly if not part of the repaired D0 experiment.

The reviewer traced transaction identity, private LFS handoff, upload ordering, cancellation and evidence limits. Real Git and real endpoint assertions are useful. All 13 final capacity fingerprints matched the inspected files. Earlier failed observations were preserved. Prototype RSS/materialized-content costs and unverified production/platform behavior were accurately qualified. These strengths do not override the path-policy blocker.
