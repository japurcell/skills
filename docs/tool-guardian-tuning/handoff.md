# Tool Guardian tuning handoff

## Goal and next step

Implement every milestone in `docs/tool-guardian-tuning/ExecPlan.md` on private branch `codex/tool-guardian-tuning`. All harmless preserved cases must allow; real operations must retain protection; no measurable full-hook latency regression. User runs installation later. Continue the active implementation session.

**Next step:** monitor `/root/optimization_proof` during its exclusive correctness/timing window, enforce its 2026-10-01 23:54:35 UTC deadline, then grant `/root/milestone_3` the public validation window for the reopened latency repair. Milestone 4 source and evidence are integrated. Preserve exclusive timing while startup worker edits its isolated candidate.

## Current state

- Base worktree: `/Users/adam/.codex/worktrees/e61c/skills`, branch `codex/tool-guardian-tuning`, HEAD `84eae394` before this checkpoint update. Initial checkpoint committed at a58f8c58; this document remains a living checkpoint. Milestones 1 and 2 complete; milestone 3 implementation integrated but latency acceptance fails; milestone 4 correctness/resource evidence integrated; milestone 5 open.
- Integrated shell/Python source: `0003737c`; common-helper lazy subprocess import: `96d4eecc`. Preserve all security and resource repairs.
- Milestone 4 integrated at `84eae394` after conflict-free rebases and identical topic/tested branch tips. Its resource fixes, boundary suites, registry, resource benchmark, raw failed B/C/C/B reports, successful finite resource report and hashes are now on base. Owned clean worktree and branch removed. No test rerun after conflict-free rebase. Overall latency acceptance remains open.
- Resource CLI ran after final paired timing, using approved native macOS collector: 90 scenarios, 25 samples, three warmups each, all decisions and 500 ms ceiling passed. Maximum first/measured sample 60.986583 ms; maximum peak RSS 28229632 bytes. Retained report `docs/tool-guardian-tuning/evidence/final-resources.json`. This finite envelope does not prove a universal pre-JSON-decoding memory cap.
- Paired final reports in milestone 4 `docs/tool-guardian-tuning/evidence/final-{baseline,candidate}-{1,2}.json` all have 147 scenarios, 25 samples, three warmups, four-worker clean batches, frozen scripts, no overlapping probes. **Latency gate fails:** clean paired median deltas Copilot +3.053/+4.906 ms, Gemini +3.667/+3.210 ms, Codex +2.157/+3.426 ms. Baseline spans 0.807/0.799/0.655 ms. 135/147 cases have positive median deltas both times; large-input speedups cannot offset this. Complete descriptive comparison `docs/tool-guardian-tuning/evidence/final-comparison.json`. Earlier `shell-candidate-{1,2}.json` also fail; retain failure evidence.

## Active workers and exclusive timing

- `/root/optimization_proof`: owns `/private/tmp/tool-guardian-optimization-proof`, branch `codex/tool-guardian-optimization-proof`, based f47d51dd. Owns proof notes/helper only, no guardian source. Frozen variants `/private/tmp/tool-guardian-ablation-final-m4`. Public controls must pass before timing: all 144 corpus checks plus shell role, Windows spelling and option-terminator controls. Compare final helpers against pre-lazy-import helpers at `5f1aa7e5`; compare only rm/git matcher bodies against unchanged `9bcc6ff5`. Keep shared quote-aware representation unchanged. Four alternating focused full-hook runs per optional group, 25/3 samples, raw evidence. No artificial uncached work. Revert optional complexity without measurable benefit through its original implementation node. Static concern about `rm -- -rf /` remains a hypothesis, not a finding. Explicit exclusive measurement permission granted at 23:38 UTC.
- `/root/milestone_3`: reopened original latency node in `/private/tmp/tool-guardian-latency-repair`, branch `codex/tool-guardian-latency-repair`, based f47d51dd. Deadline 2026-10-02 00:07:00 UTC, 30 minutes. Approved normal provider-local generated `helpers/tool_guard_policy.py` extraction: byte-identical provider-neutral policy, provider adapters retained in entrypoints, explicit public re-exports, normal Python bytecode caching. Scope includes manifest/generator contracts and explicit Codex installer helper copying with disposable install tests. Source edits allowed; public probes/tests remain paused until optimization worker releases window. Cold/no-bytecode startup must be reported separately. No self-managed bytecode caches, blanket interpreter exemptions, or represented-operation execution. Worker must read installer guidance before edits.
- Reviews `/root/native_review` and `/root/final_security_review` timed out. They supply no final approval. Final review has verified partial findings already repaired. Do not create repeated replacement reviews to evade retry limits.

## Verified behavior and limits

Milestone 4 source passes macOS Python 3.14.6: corpus 144 checks, shell 11 methods, native 13, limits 16, banners 13, generator 25, benchmark CLI 2, registry 14, all three Bash guard suites, generation freshness 26 outputs. Python 3.13.14 passes corpus/shell/native/limits. Native Windows host unavailable; skips or simulated Windows branches are not proof.

Canonical policy: `hooks/families/tool_guard.py`; generated `.codex/hooks/tool-guard.py`, `.copilot/hooks/scripts/tool-guard.py`, `.gemini/hooks/scripts/tool-guard.py`. Final private generated Codex anchors: native normalization :707, lazy structural traversal :735, Python preflight :1050, strict/Python/shell paths :1246/:1258/:1310, main :1693. Regenerate through `scripts/generate-hooks.py --write`, never hand-edit generated output.

Bounds: native aggregate 65536 UTF-8 bytes including keys/metadata; unknown/strict and aggregate executable normalized bytes 32768; normalized delete/move path aggregate 32768; structure depth32/nodes256/strings128; executable depth16/commands128/aggregate strict matcher tokens256; Python lexical tokens1024/syntax depth32/AST depth32/nodes2048/literal and resolved bytes32768. Some parser guards are dominated by earlier reachable limits; do not claim isolated maximum tests for unreachable bounds. Native bodies/search patterns are data only under exact validated schemas. Unsupported tools/extra fields remain strict.

Known source-removal policy applies to validated patch delete/move sources; no general destination protection. Saved script contents are not scanned when invoked. The guardian is not a general code security analyzer. Raw common reader decoding can precede bounded inspection, so arbitrary raw JSON memory remains outside this repair. Codex and Copilot deadlines10s; Gemini no explicit configured deadline. 500ms resource ceiling derives from 3.72 times retained existing-workload max134.263375ms.

## Findings, corrections, durable failures

- Independent reviewer reproduced execution-preserving pipeline wrappers, wrapped Python constant-concat execution sinks, and Python/shell command-option bypasses. Original worker repaired all with public red-to-green controls. Final strict path uses shared inline operand extraction; later stale duplicate finding was checked and dismissed. Do not weaken these protections for speed.
- Native normalization overflow, eager large-list traversal, Python adjacent-literal preflight overflow, and quoted/unproved token accounting reproduced and repaired in private M4. Truthful Gemini banner overflow now uses >65536 for recognized native writes; unsupported32768 coverage stays.
- Initial native review had no verified artifact; final security review timed out with partial findings. Neither is approval.
- `/usr/bin/time -l` inside sandbox exits1 after valid hook output: `time: sysctl kern.clockrate: Operation not permitted`. Harmless approved probe succeeds; unchanged approved resource run passed. Diagnose wrapper stderr before blaming hook. Timing samples exclude time wrapper; separate RSS uses macOS bytes.
- Startup-repair follow-up mistakenly included routing metadata in task prompt. Root disclosed this and must record that continuation routing_compliant:false. Model was explicitly applied at original spawn. All other task prompts keep routing metadata outside. Executed model/effort unconfirmed by runtime.
- RTK database initially unwritable; use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk ...` consistently. Do not change global user config. Git metadata needs approved escalation because actual shared git directory is outside writable root. No automatic review rejection occurred.
- Installed old guardian can reject large multiline source construction with command_segments129; use small writes, never disable or bypass real hooks.
- Copilot/Gemini Bash suites emit existing readonly observability DB diagnostics despite passing guard assertions. Do not claim installed observability works. Required checks must not be weakened.

## Remaining integration and final doc pass

Only isolated implementers change source. Root coordinates, updates plan/checkpoint, validates and integrates serially. Milestone 4 reports retain honest failed-latency comparison plus successful resource report. New runtime optimization requires affected correctness and repeated full-hook evidence; exit0 alone never means latency pass.

At end of entire session activate `update-agent-docs` **once** before `.agents/` edits, then `okf-authoring`. Fresh milestone 5 implementer should synchronize hooks/scripts instructions, known issues, testing, FILE_MAP/API_MAP/INDEX as applicable; preserve installed-old-hook workaround until user installs. Protected AGENTS sections unchanged. Record actual limits, gates, review limitations, full dispatch audit in plan. No formal doc pass has run yet.

Follow explicitly invoked `execplan-implement` skill: fresh implementer per new task-graph node; reuse only original-node repairs; own private worktrees; conflict-free rebase then serialized fast-forward; remove owned integrated clean branches/worktrees; no pushes. Existing completed owned worker worktrees already removed. Preserve unrelated worktrees.

Commit guidelines: Conventional title <=72 characters, Summary/Rationale/Tests bullet sections, trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`. Never use an em dash. RTK prefix mandatory. Persisted docs use normal prose despite terse chat. User asked save this feature checkpoint and then continue, not stop.

Final delivery only after gates pass: branch ready for review; source/generated/tests/evidence committed; real hooks not installed; Windows proof unavailable; user command `rtk proxy ./scripts/install.sh`, then review changed non-managed Codex definitions through `/hooks`. Keep live installed validation distinct.
