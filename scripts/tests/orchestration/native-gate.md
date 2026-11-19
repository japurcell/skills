# Native model-gate replay

Run the fixture from the repository root with the existing authenticated Copilot CLI. Each run directory must be new. The runner records its exact argv and scoped `write`, `policy38`, `route38`, and delegate-only `scheduler38` permissions in `private/`.

```sh
rtk proxy python3 scripts/tests/orchestration/run_native_gate.py \
  --caller delegate --parent-model gpt-6-luna --timeout-seconds 300 \
  --run-dir /private/tmp/todo38-1795057091956/copilot/native-smoke-unique --run
```

For P1, pass the rendered caller skill using `--caller-skill-file` and keep the router skill, project hook, worker profile, task, parent model, timeout, and command permissions fixed within matched pairs. Use `--caller execplan` for the other caller. Its allowed project command list omits `scheduler38`.

Re-grade a saved run without contacting a provider. The grader reads raw native events privately, strips prompts and message bodies, and reports behavior failures, record failures, unavailable observations, and unverifiable free-form actor statements separately. It accepts the actor-written `coordination.json`; malformed JSON, including valid JSON followed by trailing text, leaves native behavior grading intact while recording the input error. Shell invocations are recognized when captured as a command string or argv list. Missing native worker identity/model stays unavailable; a constrained actor statement can report its chosen model without claiming native exposure.

```sh
rtk proxy python3 scripts/tests/orchestration/grade_native_gate.py \
  --events /private/tmp/<run>/private/events.jsonl \
  --manifest /private/tmp/<run>/private/manifest.json \
  --router-log /private/tmp/<run>/private/router-events.jsonl \
  --coordination /private/tmp/<run>/project/coordination.json
```

The 18-test offline suite covers the permitted fallback, denied primary, missing evidence, malformed actor records, wrong worker types even when a matching display name is supplied, shell string/argv invocation equivalence, explicit unknown worker identity/model, constrained and unverifiable fallback records, actor-record/native-trace mismatch, background result lookup by worker ID, native pre/post coordination writes, and execution of a non-executable frozen router script through the executable `route38` alias.

```sh
rtk proxy python3 scripts/tests/orchestration/test_native_gate.py
```

P0 smoke evidence is under `/private/tmp/todo38-1795057091956/copilot/native-smoke-delegate-corrected/`. The actual frozen router returned the pinned primary and explicit fallback; one authenticated Copilot run made zero primary attempts, started one allowed fallback worker, and returned `73` from the matching worker read. Native worker model and effort are reported only when exposed by host events. Keep raw event/log directories private; share `private/verdict.json` for the compact result.
