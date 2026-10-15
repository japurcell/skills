# T2: source launch-mode contract evidence

Observed on 2026-10-15 in `/Users/adam/.codex/worktrees/design-b-t2/skills`, private branch `codex/design-b-t2`, starting at `074ca4fab21f081cbd1cbde9bf5f5ebdbdfa4d58`. T2 implements retrospective candidate 3. The user confirmed the generated-provider JSON entrypoint seam through the coordinating agent. Shared plan, generated hooks, installers, registry, and KB are outside this node's ownership.

## Contract and retained tests

`RecoveryTests.test_launch_honors_scan_mode` and `RecoveryTests.test_launch_honors_guard_mode` each cover Codex, Copilot, and Gemini in block and warn modes: 12 cases total. Every case uses `setup_fixture`, `envelope`, and the real subprocess in `launch`, with both inherited mode variables opposite the requested mode. The launch helper's existing assignments remain unchanged.

Scanner input contains a runtime-constructed fake classic GitHub token in a fresh temporary repository. Guardian receives the existing protected force-push fixture only as JSON input; the described operation is never executed. Native block responses deny; warning responses permit and may carry a nonempty `systemMessage`. Each fresh fixture asserts no existing security log, exactly one resulting record, the requested mode, matching enforcement, findings, successful audit, and the expected `github_classic_pat` pattern or `force_push_protected_branch` rule. Provider-specific Guardian log paths stay inside the disposable root.

The existing helper-failure method now explicitly verifies missing/corrupt scanner audit and Guardian policy helper denial in both modes for all providers. Diagnostic requests retain the existing deny-only assertions, including overflow/fault scenarios. No test was deleted, skipped, or weakened.

## Vertical red and green observations

The scanner slice was added first. In a disposable copy, removing only `"SCAN_MODE": mode, ` from `launch` made the focused scanner method exit 1 with six native permission assertion failures, one per provider/mode. The unchanged source helper then passed that method (one unittest method, six subcases, 0.978 seconds).

The Guardian slice followed. Removing only `, "GUARD_MODE": mode` in a separate disposable copy made its method exit 1 with the same six native permission failures (0.351 seconds). The first source green attempt failed with four `JSONDecodeError` errors because Codex/Copilot use text-prefixed audit JSON. The test parser was corrected to the existing `test-security-reporting.py` convention of decoding from the first `{`; production code and assertions were not weakened. Guardian then passed all six subcases (0.343 seconds). This was a test-authoring correction, not an observed hook defect.

Final mutation verification was rerun against the completed test source using the command below. Each iteration constructs a different disposable source copy, removes exactly one assignment, and requires all six provider/mode failures. The wrapper exits 0 only after observing both expected child exit-1 results. Copied source and temporary homes/logs are deleted on exit; the working helper is never changed.

```sh
rtk proxy python3 - <<'PY'
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
root = Path.cwd()
for assignment, method in (
    ('"SCAN_MODE": mode, ', 'test_launch_honors_scan_mode'),
    (', "GUARD_MODE": mode', 'test_launch_honors_guard_mode'),
):
    with tempfile.TemporaryDirectory(prefix='t2-mode-mutation-') as directory:
        copy = Path(directory)
        (copy / 'scripts').mkdir()
        for name in ('test-hook-diagnostic-recovery.py', 'hook_test_support.py'):
            shutil.copy2(root / 'scripts' / name, copy / 'scripts' / name)
        for relative in ('.codex/hooks', '.copilot/hooks/scripts', '.gemini/hooks/scripts'):
            shutil.copytree(root / relative, copy / relative)
        test = copy / 'scripts/test-hook-diagnostic-recovery.py'
        source = test.read_text()
        assert source.count(assignment) == 1
        test.write_text(source.replace(assignment, '', 1))
        result = subprocess.run([sys.executable, str(test), 'RecoveryTests.' + method], cwd=copy, text=True, capture_output=True)
        assert result.returncode == 1, result.stdout + result.stderr
        assert 'FAILED (failures=6)' in result.stderr, result.stderr
        assert result.stderr.count('AssertionError:') == 6, result.stderr
        for provider in ('codex', 'copilot', 'gemini'):
            for mode in ('block', 'warn'):
                assert f"(provider='{provider}', mode='{mode}')" in result.stderr
        print(method + ': child exit 1; six native permission assertion failures; mutation killed')
PY
```

Observed final output:

```text
test_launch_honors_scan_mode: child exit 1; six native permission assertion failures; mutation killed
test_launch_honors_guard_mode: child exit 1; six native permission assertion failures; mutation killed
```

## Verification results

Commands run serially from the T2 worktree:

| Command | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_scan_mode` | Exit 0; six scanner subcases pass. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_guard_mode` | Exit 0 after audit framing correction; six Guardian subcases pass. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_helper_failures_preserve_report_and_common_needs_human_cli` | Exit 0; both modes retain missing/corrupt helper denial and diagnostics. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | Exit 0; all 15 methods pass in 59.698 seconds. |
| Python AST parse of the modified test file | PASS. |
| `rtk git diff --check` | Exit 0. |

## Review and limitations

The coordinating agent reviewed correctness, security, readability, architecture, and performance with no blocking findings. Source production hooks and their generated outputs are unchanged. These mode tests prove public generated source subprocess behavior on macOS with Python 3.14.6. The existing full-suite recovery installer cases supply isolated installation/launcher evidence only. No real-home deployment, authenticated provider delivery, trust change, native Windows execution, Git publication gate semantics, or performance acceptance is claimed. The primary agent owns subsequent integration, plan reconciliation, and the single coordinated knowledge-maintenance pass.
