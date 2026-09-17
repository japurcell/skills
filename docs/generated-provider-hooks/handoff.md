# Gemini `AfterAgent` live-validation handoff

## Goal

Finish the two environment-dependent checks for generated provider hooks:

1. confirm Gemini CLI is installed and record its deployed version;
2. prove that this deployed CLI invokes the installed `AfterAgent` hook after a real turn.

These checks validate the installed application, not repository source alone.

## Status

- Feature implementation is complete on `main`.
- Real-home backup and installer smoke-test steps passed.
- `./scripts/install.sh` installed the current files without error.
- Generated-hook freshness reported 22 current files.
- Installed-copy comparisons and executable checks passed.
- The remaining work requires a session where `gemini` is installed and can authenticate.
- Repository state when this handoff was written: `main` at `daadf135903fa33626afa7297e9057a64e91de18`.

## Next step

Open a terminal on the machine where Gemini CLI is installed. Change to this repository, then complete Steps 1 through 4 below in order.

## Step 1: Verify the deployed Gemini CLI

Run these commands in the normal shell, not inside Gemini:

```bash
cd /Users/adam/dev/skills
command -v gemini
gemini --version
node --version
```

Expected results:

- `command -v gemini` prints an executable path.
- `gemini --version` prints the exact deployed version. Save this value with the test result.
- Node.js should be version 20 or newer when Gemini CLI was installed through npm.

If `gemini` is missing, install the current stable CLI using the official npm package, then repeat the three checks:

```bash
npm install -g @google/gemini-cli@latest
gemini --version
```

Official references:

- Installation: <https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/index.md>
- Current releases: <https://github.com/google-gemini/gemini-cli/blob/main/docs/changelogs/latest.md>

## Step 2: Confirm the installed hook definition

Run:

```bash
jq -e '.hooks.AfterAgent | length > 0' "$HOME/.gemini/settings.json"
test -x "$HOME/.gemini/hooks/scripts/send-event.py"
echo "Installed AfterAgent hook is present and executable"
```

The first command should print `true`. The final message should print only if both checks succeed.

The installed definition comes from `.gemini/global-settings.json:240-253`. It runs `send-event.py` with `OBSERVABILITY_CAPTURE_EVENT=true` and `OBSERVABILITY_SOURCE_EVENT_NAME=AfterAgent`.

## Step 3: Run one real Gemini turn with an isolated probe log

Create a temporary location for this probe:

```bash
probe_dir="$(mktemp -d "${TMPDIR:-/tmp}/gemini-after-agent.XXXXXX")"
probe_log="$probe_dir/observability.ndjson"
touch "$probe_log"
echo "Probe log: $probe_log"
```

Start Gemini while directing hook observability into that file:

```bash
GEMINI_OBSERVABILITY_LOG_PATH="$probe_log" gemini
```

Now the terminal is inside Gemini. Perform these actions there:

1. Enter `/hooks list`.
2. Confirm an enabled `AfterAgent` hook references `send-event.py`.
3. Enter this prompt exactly:

   ```text
   Reply with exactly AFTER_AGENT_PROBE
   ```

4. Wait until Gemini prints its final response.
5. Exit Gemini with Ctrl-D.

Official hook behavior says `AfterAgent` fires once per turn after the final response. Its input includes `prompt_response` and `stop_hook_active`: <https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md#afteragent>.

## Step 4: Inspect and classify the result

Back in the normal shell, run:

```bash
jq -c '
  select(
    .source_event_name == "AfterAgent" and
    .event_name == "agent_stop"
  )
  | {
      source_event_name,
      event_name,
      hook_name,
      session_id,
      outcome
    }
' "$probe_log"
```

### Pass

The command prints at least one JSON object containing:

```json
{"source_event_name":"AfterAgent","event_name":"agent_stop"}
```

Extra fields are expected. Record the Gemini version and this result as live deployed proof.

### `AfterAgent` delivery failure

If the filter prints nothing, inspect all captured event names:

```bash
jq -r '[.source_event_name, .event_name, .hook_name] | @tsv' "$probe_log"
```

If other events appear but `AfterAgent` does not, hook loading works but this CLI version did not deliver `AfterAgent`. Record:

```bash
gemini --version
```

Then note the failed live capability probe. Do not treat simulated repository tests as proof of event delivery. Upstream issue: <https://github.com/google-gemini/gemini-cli/issues/27712>.

### No events captured

If the log is empty, check configuration and hook enablement:

```bash
wc -l "$probe_log"
jq '.hooksConfig, .hooks.AfterAgent' "$HOME/.gemini/settings.json"
ls -l "$HOME/.gemini/hooks/scripts/send-event.py"
```

Restart Gemini after any settings change. Inside Gemini, use `/hooks list` again. Official command reference: <https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/commands.md#hooks>.

## Verification state to record

Record all four items before closing the next session:

- exact `gemini --version` output;
- whether `/hooks list` showed the installed `AfterAgent` hook enabled;
- whether the probe log contained `source_event_name=AfterAgent` and `event_name=agent_stop`;
- probe log path or the relevant filtered JSON record.

Keep `probe_dir` until the result is recorded. Afterward, it can be removed with:

```bash
rm -r -- "$probe_dir"
```

## Constraints and known issue

- Do not edit repository hook output files during this probe.
- Do not infer live delivery from `scripts/test-gemini-hooks-observability.sh`; that suite verifies the provider envelope and installed script behavior, not Gemini CLI event dispatch.
- Gemini CLI issue `#27712` reported missing `AfterAgent` execution in version `0.45.0` and related builds. Live proof is required for the deployed version.
- After completing the probe, update this handoff with the version, result, and any failure evidence.
