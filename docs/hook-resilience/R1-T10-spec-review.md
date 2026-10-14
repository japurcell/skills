# R1 T10 Spec supplement

Independent review on 2026-10-14 at `864bbda0`: **no actionable findings.** T10 implements the three accepted D2 changes without expanding scope or changing profiles, enforcement policy, report limits, attribution, or audit-failure behavior.

Independent checks passed:

- 5,243 chunked collector cases against JSON syntax and explicit depth expectations.
- 60 public scanner/Guardian cases across all providers covering retained pipes, split escapes and UTF-8, later dangerous commands, invalid roots, malformed syntax, trailing data, and excessive depth.
- 1,196 label comparisons against the prior regex behavior.
- 15 public embedded-token, normalization, clipping, and audit-failure cases.

The POSIX helper restores descriptor flags through `finally`, distinguishes timeout from EOF, and retains bounded readiness fallback. Structural scanning preserves escape adjacency and leaves full syntax validation to `json.loads`. The ASCII prefilter covers every regex alternative; normalized non-ASCII labels retain regex authority.

One initial probe assertion incorrectly required whole-label replacement from Guardian's unchanged non-ASCII branch. That branch safely redacts credentials while retaining surrounding text; the corrected check passed.

Original P1/P2 remain closed. All probes have finished; no test processes remain. No benchmarks or full aggregate suite ran. Native Windows and authenticated provider delivery remain unverified, and final release performance acceptance remains separate.
