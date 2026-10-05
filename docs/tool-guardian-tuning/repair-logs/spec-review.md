# Tool Guardian repair: original Spec reviewer work log

## Scope and current state

I am the original Spec reviewer from the 2026-10-05 review of fixed point `9bcc6ff56cf916f848e4b32314ded35757d240c2` through `4bade608b9483944e69da0e424f10d113f011012`. The user requested re-review until the findings close. My write ownership is this log only. Root owns the plan and shared documentation; the repair agent owns source, generated outputs, and tests. I will not change installed hooks, invoke represented dangerous operations, run overlapping timing probes, or delegate further work.

Preparation and both frozen re-review rounds are complete. Round 2 closes the original Spec findings. No unfinished repair source was reviewed, and no tests or benchmarks ran during preparation.

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

Round 2 closes the original Spec findings with no new actionable issue found. Root owns integration, separate frozen performance validation, shared handoff synchronization, and the single formal documentation pass at the end of the overall source-edit session. Any later runtime change requires review of the affected behavior before relying on this verdict.

## Re-review round 1, 2026-10-05

Candidate: `94704adb807df98989471bee292e7dc61b4fc377`, clean isolated checkout `/private/tmp/tool-guardian-review-repair`, repair base `4bade608b9483944e69da0e424f10d113f011012`. All review commands used this checkout and `login:false`, with `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy` as the shell prefix. Python suite and probe invocations used `python3 -B`; the native suite, corpus suite, and probes additionally set `PYTHONDONTWRITEBYTECODE=1`. No generator, installer, timing probe, or represented operation ran.

Exact focused diff command: `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy git diff 4bade608b9483944e69da0e424f10d113f011012...94704adb807df98989471bee292e7dc61b4fc377 -- hooks/families/tool_guard.py scripts/test-tool-guard-limits.py scripts/test-tool-guard-shell-data.py`. I read the shared milestone 6 and my existing log. An initial read guessed the worker log name `implementation.md` and returned file-not-found. `rtk proxy rg --files docs/tool-guardian-tuning/repair-logs` in the isolated candidate located `repair-worker.md`, which I then read successfully. This was a documentation lookup error, not a failed validation.

Independent suite commands and results:

- `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-limits.py`: 17 tests passed, exit 0.
- `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-native-data.py`: 13 tests passed, exit 0.
- `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-false-positives.py --script-root /private/tmp/tool-guardian-review-repair --expected-behavior candidate`: 144 public fixture checks passed, zero failures, exit 0.

An independent `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B -` heredoc imported the maintained corpus helper and invoked only generated hooks using `subprocess.run([sys.executable, '-I', '-S', '-B', str(script_path(Path.cwd(), provider))], input=encode(envelope(provider, fixture)), capture_output=True, env=env, timeout=5)`. Every invocation used disposable home, guardian-log, and audit-log paths, with skip and allowlist variables removed. This exercised 31 independently constructed cases across all three providers and both modes: 186 checks, zero failures. Its per-case results are `/private/tmp/tool-guardian-spec-round1-public-results.json`.

The 31 cases included downloader fixtures with `cat`, `tee copy.sh`, `head`, and `cat` followed by `sort`; shell positional execution through `exec` and direct argument expansion; the accepted conservative positional-data fallback; safe positional arguments; proven literal search bodies; a quoted literal pipeline; the original normalization overflow; exact normalized maximum and first overflow; and spaced/attached unresolved Python options behind plain, wrapped, and unresolved-prefix launchers. Policy threats denied in block mode and warned in warn mode; incomplete inspection and aggregate overflow denied in both modes; harmless controls allowed silently.

### Closure decisions

- **R1 remains open.** The original adjacent and intermediate installer reproductions now produce correct decisions. However, the related inherited-stdin consumer case below still silently allows. Canonical `hooks/families/tool_guard.py:1355` removes the inspected inline shell body, `:1361` builds pipeline text from only the remaining words, and `:1377-1378` applies the pipeline matcher without the body consumer. Body inspection at `:1350-1352` has no incoming producer context.
- **R2 original finding closed.** Canonical `hooks/families/tool_guard.py:1353-1365` keeps unproved positional arguments in strict inspection after separately inspecting the body. Independent shell argument variants denied or warned as required. Safe argument and proven search-body controls stayed silent. The accepted strict-fallback tradeoff was preserved; no additional positional-data exemption was requested.
- **R4 closed.** Canonical `hooks/families/tool_guard.py:762-766` charges normalized UTF-8 length and returns raw source. The original 46,218-byte normalized aggregate denied in block and warn modes. The exact 32,768-byte aggregate allowed silently and the first 32,769-byte aggregate denied, including maintained tests with matching allowlists. All 17 resource tests passed.
- **R3 related checks pass.** Canonical `hooks/families/tool_guard.py:1226-1232` recognizes attached Python code before dismissing nonliteral options and recognizes attached code after unresolved option prefixes. Independent spaced and attached dynamic operands denied in both modes across all three providers. R3's original reviewer retains ownership of its closure verdict.

### Related actionable R1 finding

P1: an inline shell consumer can still execute downloaded stdin while disappearing from pipeline matching. Construct the public command without executing it:

```python
from tool_guard_corpus import OPERATIONS
pipe = chr(124)
command = OPERATIONS['download_execute_bash'].replace(
    pipe + ' bash', pipe + ' cat ' + pipe + " sh -c 'bash'")
```

The shell command-option body launches the Bash consumer, which inherits the producer's piped stdin. All three frozen candidate hooks silently allowed this in both block and warn modes, six checks total, with exit 0 and empty stderr. A paired variant using the other downloader and shell family still produced the expected deny/warning, so the gap depends on the removed consumer text.

A second independent Python heredoc copied the original fixed-point provider entrypoints and their `common.py`/`audit.py` helpers using `subprocess.check_output(['git', 'show', base + ':' + str(filename)])` into a disposable root, with `base = '9bcc6ff56cf916f848e4b32314ded35757d240c2'`. It invoked the same fixture through every copied hook and both modes. All three original baseline hooks denied the installer rule in block mode and emitted the corresponding warning in warn mode, six checks total. No represented downloader or interpreter pipeline executed.

This violates milestone 6's requirement to preserve producer input feeding an interpreter and the original requirement to preserve installer-pipeline protections. Retain or propagate the executable consumer role when inspecting inline shell bodies, while keeping proven data exemptions. I sent the finding and baseline confirmation promptly to root. The Standards reviewer independently reported the same gap without the `cat` intermediary.

### Identity and verdict

`RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy git rev-parse HEAD` confirmed the candidate commit. `rtk proxy git status --porcelain=v1` was empty before and after the initial validation. A Python SHA-256 manifest of 158 tracked hook/source/test files was saved before review to `/private/tmp/tool-guardian-spec-round1-before.json`; after the independent 186-check probe, all 158 hashes matched. No source or test edits were made.

Round 1 verdict: changes requested for the related R1 execution-flow gap. Original R2 and R4 close; original R1 examples pass but the finding remains open until the related consumer variant is repaired and re-reviewed. The incident corpus and native suites preserve established proven exemptions. Performance acceptance and platform/live proof remain separate and pending.

## Re-review round 2, 2026-10-05

Frozen candidate: `27062fc6b3b9c9a86e8f6d8838c3926a674faad0`, in the same isolated `/private/tmp/tool-guardian-review-repair` checkout. It preserves initial repair commit `94704adb807df98989471bee292e7dc61b4fc377`. I read the worker's round 2 log and this review log, and inspected both source diffs with these exact commands:

- `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy git diff 94704adb807df98989471bee292e7dc61b4fc377...27062fc6b3b9c9a86e8f6d8838c3926a674faad0 -- hooks/families/tool_guard.py scripts/test-tool-guard-shell-data.py`
- `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy git diff 4bade608b9483944e69da0e424f10d113f011012...27062fc6b3b9c9a86e8f6d8838c3926a674faad0 -- hooks/families/tool_guard.py`

Commands used the isolated checkout and `login:false`. The initial identity check used `subprocess.check_output(['git', 'rev-parse', 'HEAD'])` and `subprocess.check_output(['git', 'status', '--porcelain=v1'])` inside `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B -`. It confirmed the supplied candidate and clean status. The same heredoc fingerprinted 158 tracked source, hook, and test files with SHA-256 and retained `/private/tmp/tool-guardian-spec-round2-before.json`.

Independent suite commands:

- `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-limits.py`: 17 tests passed, exit 0.
- `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-native-data.py`: 13 tests passed, exit 0.
- `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B scripts/test-tool-guard-false-positives.py --script-root /private/tmp/tool-guardian-review-repair --expected-behavior candidate`: all 144 public checks passed, zero failures, exit 0.

An independent `PYTHONDONTWRITEBYTECODE=1 RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 -B -` heredoc used the same isolated public-hook invocation and disposable-log harness recorded for round 1. It constructed 49 cases and exercised each through all three providers in block and warn modes: 294 public checks, zero failures. Each check required exit 0, empty stderr, the expected decision, and correct warning presence or silence. Limits and unresolved code additionally required their expected rule identities. Results are retained at `/private/tmp/tool-guardian-spec-round2-public-results.json`.

The independent cases covered the original downloader fixtures with `cat`, `tee`, `head`, and chained intermediates; the exact round 1 inherited-stdin case with and without `cat`; nested shell, `exec`, `command`, `eval`, and Python execution-sink consumers; shell and Python producers before the real outgoing pipe; search output shared by sequential commands before an inline consumer; original positional execution and accepted conservative positional fallback; attached dynamic Python operands; and normalized maximum, first overflow, and original 46,218-byte overflow. Harmless controls covered safe positional arguments, safe printing, quoted literal pipe text, incoming nested searches, search-plus-print, eval/search, proven writers, writer-plus-print producers, and both fixed guardian survey forms. Only the hook processes executed.

### Final closure decisions

- **R1 closed, including the related round 1 gap.** Canonical `hooks/families/tool_guard.py:1353-1356` carries inspected body context into the outer invocation; `:1372-1375` places it before the real outgoing pipe; `:1386-1390` passes retained context to outer matching. Nested Python execution sinks forward context at `:1211-1215`. Inherited executable-output roles apply to sequential child commands at `:1283-1289`. The original intermediate and inherited-stdin cases now deny in block mode and emit the expected policy warning in warn mode across all providers. Nested producer and sequential-search variants also pass. Established proven search, writer, and survey data contributes no pipeline context, and the corresponding safe controls remain silent. Literal pipe values are masked at `:1367`; parsed operators retain their role at `:1375`.
- **R2 remains closed.** Canonical `hooks/families/tool_guard.py:1358-1371` preserves unproved positional arguments after inspecting the body. Independent direct argument execution and printing controls retain the accepted strict fallback; safe arguments and established proven forms still allow. No general positional-data proof or blanket interpreter ban was added.
- **R4 remains closed.** Canonical `hooks/families/tool_guard.py:762-766` still charges normalized UTF-8 aggregate bytes while returning raw source. The exact 32,768-byte normalized aggregate allows, 32,769 denies, and the original 46,218-byte aggregate denies in both modes. The independent 17-test limits suite also preserves warn-mode and valid-allowlist precedence for incomplete inspection.
- **R3 related controls still pass.** The attached and spaced unresolved Python forms, including wrapped and unresolved-prefix launchers, deny in both modes. Original R3 closure remains the Standards reviewer's responsibility.

The final comparison of all 158 source/test fingerprints found no change. `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy git status --porcelain=v1` remained empty after validation. No source, test, generator, installer, hook configuration, or timing evidence was modified. My only repository edit is this shared-root log. No new validation errors or actionable findings occurred in round 2.

Final Spec verdict for `27062fc6`: approve within the reviewed correctness scope. Original R1, R2, and R4 are closed, related execution-context behavior preserves the agreed strict-fallback boundary and tested proven exemptions, and no new actionable Spec issue was found. This does not establish performance acceptance, native Windows execution, installed behavior, or provider-delivery timing; root owns the remaining validation and documentation gates.
