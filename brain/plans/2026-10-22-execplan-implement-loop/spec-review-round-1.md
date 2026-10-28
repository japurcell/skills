# Spec review, round 1

Pinned source: `4729b39fda6da38e020deedc7085bad29cb40cf1`, base `e231bcc35b44d42c12f86b8893f514468dfc5f31`; both resolve. Source paths below are relative to `skills/default/execplan-implement-loop/`. Spec is `brain/plans/2026-10-22-execplan-implement-loop/ExecPlan.md`.

1. **[P2] Preserve a recovery barrier after helper death during doctor.** Source `scripts/qualify.py:426-443`, `599-657` considers only existing runner-state directories; it ignores unfinished attempts. Spec:172 says “Prevent concurrent runs”; :174 says “never starts a replacement while old children survive.” Public-CLI repro `/private/tmp/execplan-spec-repro.py`: SIGKILL the helper during its real doctor's fake-provider version check, then rerun helper without resume. It starts attempt 2 while doctor/provider PIDs `52004/52016` remain alive alongside `52031/52043`. Both manifest attempts say `starting`, `runner_started:false`. No production source was altered.

2. **[P2] Verify baseline ancestry rather than revision existence.** Source `scripts/qualify.py:819-824` treats successful `rev-list baseline..HEAD` as baseline reachability. Spec:274 requires “correct baseline/three-commit evidence”; the published guide:69 promises “baseline reachability.” Repro `/private/tmp/execplan-spec-collect-repro.py` creates an unrelated orphan HEAD retaining the baseline object: `merge-base --is-ancestor` exits 1, but collection reports `baseline_reachable:true`, `commits_since_baseline:1`.

3. **[P3] Keep standalone doctor from creating bytecode.** Source `scripts/run.py:12-13,61-62` imports local modules before disabling bytecode writes. Spec:154 says “Never ... mutate Git/files.” Repro `/private/tmp/execplan-spec-readonly-repro.py` runs the documented doctor on a fresh copied bundle: exit 0 creates four `scripts/__pycache__/*.pyc` files.

4. **[P3] Make collection Git queries read-only.** Source `scripts/qualify.py:817` calls ordinary `git status`. Spec:324 says “Doctor/collect are repeatable read-only operations.” The same read-only repro touches only the tracked plan's mtime; collection exits 0 and reports clean, but changes `.git/index` bytes through Git's optional refresh.

5. **[P3] Read the actual saved provider-version path.** Source `scripts/qualify.py:862-868` reads `provenance.provider_version`, while doctor emits `provenance.provider.version`. Spec:172 requires refreshing “baseline/version/log/status.” The collect repro uses actual helper/runner plus fake Gemini: saved version is `0.65.0`, collected `versions.provider` is null.

Five findings. All repros used disposable roots and fake providers; no paid/live calls or repository edits. No scope-creep finding.
