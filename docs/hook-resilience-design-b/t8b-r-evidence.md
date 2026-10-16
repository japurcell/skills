# T8b-R scanner registration evidence

T8b-R repairs only the registration assertions in the three maintained scanner shell suites. The accepted T8b product policy remains the source of expected registrations. The private task branch is `codex/design-b-t8b-r`, based on `419d20d5a38f4ca0284ab126ddfdbcae0aedaf79` (tree `e7feafc3ef9188db5aeecb00459a4bd7e28611dd`). This evidence file and the three suites are the complete task ownership boundary.

## Actual hosted red

Primary supplied the actual macOS failure from [run 38980469324](https://github.com/japurcell/skills/actions/runs/38980469324), exact published snapshot `0c2282f4c0f42681c229aa4bcad6a09026707f90`. Preflight, recovery, and security reporting passed. The Codex scanner step failed immediately at inline Python assertion line 9 because the existing test required automatic `scan-secrets.py` placement in `PreToolUse` and `Stop`. Source inspection found the same obsolete expectation in the existing Copilot and Gemini registration checks. This repair does not reinterpret that red as a scanner detection failure.

## Current positive assertions

Codex checks one Guardian `PreToolUse` handler with its tool matcher and one historical-status `Stop` handler, including command type, Windows command variant, timeout, and visible status field. Copilot checks Guardian and observability on `preToolUse`, status and observability on `agentStop`, and the preserved bell and observability on `sessionEnd`, including Bash/PowerShell variants, event attribution, configured modes/timeouts, and relative ordering. Gemini checks Guardian, observability, and RTK on `BeforeTool`, historical status and observability on `AfterAgent`, and preserved `SessionEnd` observability. Its status registration retains the logical `scan-secrets` name so installed disabled-hook intent can survive migration.

A source-only comparison against the task base confirms that the Codex direct scanner/capture tail is byte-identical, and both other suites retain byte-identical direct scanner test bodies and main calls except the two renamed registration checks. No findings, clean, warn/block, malformed-input, audit, timeout, redaction, mode, or native capture assertion was removed, skipped, or weakened. No product, generated registration, workflow, registry, shared plan, installer, or KB file changed.

## Static validation

`rtk proxy bash -n` passed for all three owned scripts. Parser-only `compile` checks passed for all five updated inline Python registration blocks. `rtk git diff --check` passed. These checks executed no hooks, scanners, capture suites, generators, installers, or benchmarks.

## Functional validation state

Pending explicit handoff of the serialized local functional window from primary. The proposed group runs the complete maintained Codex, Copilot, and Gemini scanner shells once each, sequentially, on Python 3.14.6. Each suite already invokes its provider capture checks. The retained logs must establish all 12 native Darwin block/warn and clean/findings evidence rows with restored soft process limits; no separate capture run is planned. Homes, configuration, temporary files, audit logs, and observability paths will be disposable, with `OBSERVABILITY_TESTING=1` and Git global configuration disabled.

Actual hosted Python 3.13 verification remains pending. Primary owns composition with the accepted T1-CI repair, publication of the exact candidate, and return of hosted logs. Local proof does not establish native Windows or authenticated provider delivery. No live-home installation, trust change, automatic checkpoint, external task-branch push, or KB pass is authorized for this task.
