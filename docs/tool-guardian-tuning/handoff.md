# Tool Guardian tuning handoff

## Goal and next step

Complete every milestone in `docs/tool-guardian-tuning/ExecPlan.md` on private branch `codex/tool-guardian-tuning`. User runs installation later. Continue this implementation session.

**Next step:** original milestone 3 implementer repairs bounded quoted-literal scanning, preserves complete inspection and reruns frozen full-hook gates. Three cold writer median violations remain. Do not raise the agreed budgets silently.

## Current state

- Policy helper extraction is integrated at `f6831fe0c314f6fd448447cc3654b442a2b43d11`, rebased without conflicts. Its clean owned worktree and branch were removed. Root preserves unrelated worktrees. No tests repeat solely for that rebase.
- Milestones 1 and 2 are complete. Shell/Python policy, resource guards and optional optimization evidence are integrated. Milestones 3/4 acceptance and milestone 5 documentation remain open.
- Current limits: per provider/case steady-state +2 ms median/+5 ms p95; fresh copy without provider bytecode +5 ms median/+10 ms p95; finite resource cases 500 ms. Full inspection, logging, fail-closed bounds and provider contracts remain mandatory. Historical zero-budget failures remain truthful under their original criterion.
- Policy extraction has byte-identical generated local helpers, explicit original exports and retained provider adapters. Both Codex installer copy lists include the helper. Missing/corrupt helpers deny in block and warn modes. Ordinary Python bytecode only; no custom cache or live-home cache changes.

## Verified checkpoint

`docs/tool-guardian-tuning/latency-repair-notes.md` and `evidence/startup-module-agreed-budget-checkpoint.json` describe the integrated extraction.

- Python 3.14.6: generator25/29 artifacts, shell12, native13, limits16, banners13, corpus144, all three provider shell suites and both disposable-home installers pass.
- Native macOS Python3.13.14: corpus, shell, native, limits and banners pass. Initial mistaken filenames remain recorded alongside corrected checks. Native Windows unavailable; PowerShell on macOS is not Windows proof.
- Four ordinary-cache reports retain correct decisions for all147cases. All medians improve in both pairings. Three isolated p95 outliers clear targeted B/C/C/B repeats.
- Full cold report `evidence/startup-module-cold-25.json`:7350 fresh-copy launches, all decisions correct, six budget violations. `startup-module-cold-repeat-25.json`:300 launches; three repeated median failures remain: Gemini writer-after+5.391ms, Codex writer-before+5.147ms and writer-after+5.344ms. Repeated p95 deltas meet+10ms. Overall acceptance FAIL.
- Resource report `evidence/startup-module-resources-25.json`:90cases25/3, all decisions correct, maximum43.097ms, peak22,331,392bytes. All39 frozen source hashes unchanged. No runtime jobs remain from that checkpoint.
- Immutable original baseline: `/private/tmp/tool-guardian-baseline`. Extraction baseline/candidate roots: `/private/tmp/tool-guardian-startup-module-baseline` and `-candidate`. Preserve source/payload/corpus/runner hashes and raw samples.
- Optional ablations integrated at `d602bbe1`:1026 public decisions and12000 warm samples. Lazy helper imports and removal/Git growth have measured benefits; mixed suffix survey regression remains recorded. Proof worker timed out before commit; root verified and retained checkpoint. No blanket performance acceptance.

## Repair boundaries and coordination

The proposed repair replaces per-character literal scans with delimiter search, preserving POSIX single-quote semantics, Python escape parity/triple quotes, malformed-input rejection and every byte/token/depth limit. Canonical changes only in `hooks/families/tool_guard.py`, then regenerate. Public end-to-end quote/backslash/substitution/heredoc controls precede source edits. Warm/cold full-hook measurements determine acceptance; parser timing alone cannot.

Original milestone3 owns this repair. Root coordinates, validates and integrates only. Independent runtime probes must not overlap measurements. A new bounded dispatch and private worktree follow integration; routing metadata stays outside task prompts. Reuse only original-node repairs. Private branches never push. Integrate serially with clean worktree, rebase, fast-forward, matching tip, then cleanup.

Final full `scripts/test-all.py` verification remains pending. At end of entire session activate `update-agent-docs` once before `.agents/` edits, then `okf-authoring`; delegate milestone5 to a fresh implementer. Synchronize hooks/scripts instructions, testing, known issues, FILE_MAP/API_MAP/INDEX as applicable. Preserve installed-old-hook workaround until user installs. Protected AGENTS sections remain intact. No formal final doc pass has run.

## Durable findings and errors

- Security review reproduced pipeline wrappers, wrapped Python sinks and interpreter options/quoted shell command names; repaired with public red-to-green controls. Do not weaken these protections. Timed-out native/final security reviews provide partial findings, not full approval.
- Recognized native bound65536bytes; unsupported/executable32768; structure depth32/nodes256/strings128; shell depth16/commands128/totaltokens256; Python syntax depth32/tokens1024, ASTdepth32/nodes2048. Some guards are dominated by earlier reachable bounds; do not invent maximum tests. Raw common-reader JSON decoding remains outside bounded post-decode inspection.
- Native content/search data is exempt only under exact validated schemas. Patch delete/move checks protect source removals under existing policy; no general destination or saved-script-content protection.
- `/usr/bin/time -l` inside sandbox fails with `time: sysctl kern.clockrate: Operation not permitted` after correct hook output. Approved harmless collector succeeds. Timing excludes RSS wrapper; native macOS RSS uses bytes.
- Use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk ...`; RTK default database is unwritable. Git metadata outside sandbox requires approved escalation. No automatic review rejection occurred.
- Generator mutable fixtures and installer checks must run serially. Gemini installed smoke needs its own directory log path, distinct from Copilot regular-file path. Assertions were preserved.
- Root cannot poll another agent's shell session; finished retained reports establish completion. Sandbox `ps` denial is not hook failure.
- One earlier startup follow-up included routing metadata in prompt; recorded routing_compliant:false. Configured model/effort explicitly applied at original spawn, executed configuration unconfirmed. Other prompts keep routing outside.
- Existing Copilot/Gemini shell suites can print readonly observability DB diagnostics while guard assertions pass. Do not claim installed observability validation.
- Never use em dash. Persisted docs/commits use normal English. Commit Conventional title<=72; Summary/Rationale/Tests bullets and Copilot co-author trailer.

## Delivery

Only report branch ready after all gates and doc pass finish. No real hooks installed. User command: `rtk proxy ./scripts/install.sh`, followed by reviewing changed non-managed Codex definitions through `/hooks`. Report native Windows verification unavailable.
