# Native model-gate replay

Prepare the fixture offline from the repository root. Each run directory must be new. The runner records its exact argv and scoped `write`, `policy38`, `route38`, `check-record38`, and delegate-only `scheduler38` permissions in `private/`.

The fixture starts `coordination.json` with two null fields. The caller fills `before` and runs `check-record38 before` prior to dispatch. After recording the receipt in `after`, it runs `check-record38 after`. The checker parses the file on disk and reports syntax or field errors. The grader still requires native evidence of caller writes on both sides of dispatch.

```sh
scratch="$(mktemp -d "${TMPDIR:-/tmp}/native-gate.XXXXXX")"
run_dir="$scratch/run"
arm=challenger2
caller=delegate-to-subagents
rendered=/private/tmp/todo38-1795057091956/p2-screen/rendered/$arm/$caller
rtk proxy python3 scripts/tests/orchestration/run_native_gate.py \
  --caller delegate --caller-skill-file "$rendered/caller-SKILL.md" \
  --router-skill-file "$rendered/router-SKILL.md" \
  --parent-model gpt-6-luna --timeout-seconds 300 \
  --run-dir "$run_dir"
```

For an intentional live trial, choose a fresh run directory and append `--allow-model-calls`. This starts authenticated Copilot and can spend tokens.

For the other caller, set `caller=execplan-implement`, set `--caller execplan`, and use that directory's rendered caller and router files. In matched pairs, vary both rendered caller and router wording as assigned. Keep the router Python/catalog, project hook, worker profile, task, parent model, timeout, and command permissions fixed. The ExecPlan caller's allowed project command list omits `scheduler38`.

Re-grade a saved run without contacting a provider. The grader reads raw native events privately, strips prompts and message bodies, and reports behavior failures, record failures, unavailable observations, and unverifiable free-form actor statements separately. It accepts the actor-written `coordination.json`; malformed JSON, including valid JSON followed by trailing text, leaves native behavior grading intact while recording the input error. Shell invocations are recognized when captured as a command string or argv list. Missing native worker identity/model stays unavailable; a constrained actor statement can report its chosen model without claiming native exposure.

The runner grades the same saved artifacts as replay. Both return exit 0 for a pass, 1 for a proven failure, and 2 when required evidence is unavailable. An unreadable event, router, or policy row prevents a pass. The verdict names the file and line and continues grading readable rows, including those after the damage. A missing receipt in a damaged trace leaves the corresponding action unverified. A readable wrong-worker dispatch still fails, even if another row is damaged. Malformed actor coordination is itself a record failure.

Copilot can return only the answer from a synchronous task. Record JSON null for an unexposed worker ID or model and for the blocker after a successful launch. Verifying this dispatch requires matching native start, configuration, and completion events for the worker. Legacy records can describe the answer-only receipt in the blocker field. Free-form unknown identity or model strings remain unavailable observations. The verdict reports the task receipt's worker ID and the actor's corroborated model separately from the native worker ID and model. For intended child controls, both `profile` and `agent_type` name the required worker and both must agree with the call when supplied.

```sh
run_dir=/path/to/saved/run
rtk proxy python3 scripts/tests/orchestration/grade_native_gate.py \
  --events "$run_dir/private/events.jsonl" \
  --manifest "$run_dir/private/manifest.json" \
  --router-log "$run_dir/private/router-events.jsonl" \
  --coordination "$run_dir/project/coordination.json"
```

The offline suite checks that both runners prepare fixtures without invoking a provider CLI. It also covers the permitted fallback, denied primary, missing evidence, malformed actor records, wrong worker types even when a matching display name is supplied, shell string/argv invocation equivalence, explicit unknown worker identity/model, constrained and unverifiable fallback records, actor-record/native-trace mismatch, background result lookup by worker ID, exact child output messages matched by worker ID, post-dispatch receipts before asynchronous completion, native pre/post coordination writes, and execution of a non-executable frozen router script through the executable `route38` alias.

```sh
rtk proxy python3 scripts/tests/orchestration/test_native_gate.py
```

P0 smoke evidence is under `/private/tmp/todo38-1795057091956/copilot/native-smoke-delegate-corrected/`. The actual frozen router returned the pinned primary and explicit fallback; one authenticated Copilot run made zero primary attempts, started one allowed fallback worker, and returned `73` from the matching worker read. Native worker model and effort are reported only when exposed by host events. Keep raw event/log directories private; share `private/verdict.json` for the compact result.
