# Tool Guardian repair: original Spec reviewer work log

## Scope and current state

I am the original Spec reviewer from the 2026-10-05 review of fixed point `9bcc6ff56cf916f848e4b32314ded35757d240c2` through `4bade608b9483944e69da0e424f10d113f011012`. The user requested re-review until the findings close. My write ownership is this log only. Root owns the plan and shared documentation; the repair agent owns source, generated outputs, and tests. I will not change installed hooks, invoke represented dangerous operations, run overlapping timing probes, or delegate further work.

Preparation is complete. Actual repair review is pending a frozen candidate supplied by root. No unfinished repair source has been reviewed, and no new tests or benchmarks have run during preparation.

The user accepted strict fallback and possible false alarms for harmless but unproved positional arguments. Re-review must preserve every established proven native, search, writer, and survey data exemption. Unsupported forms retain strict inspection; recognized unresolved execution and incomplete inspection deny even in warn mode. Additional positional-data proofs are outside this repair.

## Original Spec findings

1. **R1, P1: installer pipeline intermediates bypass protection.** At the original candidate, all three public provider entrypoints silently allowed the preserved downloader/interpreter fixtures after insertion of `cat`, `tee`, or `head`. The original baseline denied the `cat` variants. Canonical source at `hooks/families/tool_guard.py:1281` recorded only adjacent pairs, while `:1188` suppressed the original matcher using the incomplete pair map. Original ExecPlan line 226 required preservation of installer pipelines and every current rule family.
2. **R2, P1: shell positional arguments escape inspection.** A shell command-option body using `exec` and the positional argument expansion could execute the protected force-push corpus operation from its remaining arguments. All three original candidate entrypoints silently allowed it in block and warn modes. The baseline denied in block mode and emitted a warning in warn mode. Canonical source at `hooks/families/tool_guard.py:1355-1358` treated body inspection as proof for the entire invocation and omitted remaining arguments. Original ExecPlan line 224 required protections for execution hidden beside or inside apparent data. This finding also appeared on the Standards axis.
3. **R4, P2: aggregate executable accounting charges raw bytes.** A quoted shell command-option body containing `echo ` followed by 700 U+FDFA characters had a 4,218-byte raw aggregate and a 46,218-byte normalized aggregate across the outer and inner fragments. Each normalized fragment fit individually, but their aggregate exceeded the 32,768-byte contract. All three candidate providers silently allowed it, including warn mode. An ASCII aggregate of 34,018 bytes correctly denied. Canonical source at `hooks/families/tool_guard.py:762-765` validated normalized fragments separately but summed raw UTF-8 bytes. Original ExecPlan line 109 specified normalized aggregate accounting across nested fragments.

No additional scope-creep finding was verified. The original review did not identify a separate defect in the retained accepted latency evidence. R3, the attached unresolved Python code option, originated with the Standards reviewer and remains part of milestone 6; I will check interactions relevant to the Spec contract without claiming authorship of that finding.

## Preparation record

On 2026-10-05, I read the handoff skill, then the repository memory index, architecture, conventions, and repo instructions. I read `docs/tool-guardian-tuning/handoff.md` and milestone 6 in `docs/tool-guardian-tuning/ExecPlan.md`. These establish the four unique repair issues, settled strict-fallback tradeoff, independent frozen re-review, unchanged latency gates, per-agent logs, and user-owned real installation.

Read commands used `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy cat` for those files and `rtk proxy rg -n -A 50 -B 5 'Milestone 6' docs/tool-guardian-tuning/ExecPlan.md` for the current milestone. All reads succeeded. The log was created with the normal patch tool. No preparation errors occurred.

## Next step and verification state

Wait for root to supply the frozen candidate identity, relevant diff, and review window. Then independently inspect the repairs and run public-entrypoint reproductions with disposable logs, including the original failures and retained harmless controls. Record exact commands, observations, remaining findings, and closure evidence here. Performance acceptance remains root's separate frozen validation responsibility. Root will synchronize the shared handoff and perform the single formal documentation pass at the end of the overall source-edit session.
