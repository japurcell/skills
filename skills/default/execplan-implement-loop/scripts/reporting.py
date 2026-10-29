"""Bounded, deterministic diagnostics shared by every runner summary."""
from pathlib import Path
import os
import re
import shlex


DIAGNOSTIC_LIMIT = 65536


def provider_diagnostic(raw, captured_bytes, truncated):
    """Sanitize before bounding; arbitrary secrets cannot be perfectly scrubbed.

    A captured tail can start inside a credential, so omit it entirely rather
    than treat a partially captured token as safe diagnostic text.
    """
    metadata = dict(artifact_ref=None, captured_bytes=captured_bytes, retained_bytes=0,
                    truncated=truncated, encoding='utf-8-replace', redaction_status='content_omitted')
    if truncated:
        return metadata, None
    try:
        text = raw.decode('utf-8', errors='replace')
        original = text
        secrets = {value for name, value in os.environ.items() if value and re.search(
            r'token|secret|pass(?:word|wd)?|api[_-]?key|private[_-]?key|credential|auth', name, re.I)}
        for value in sorted(secrets, key=len, reverse=True):
            text = text.replace(value, '[REDACTED]')
        patterns = (
            r'(?i)\b(?:Bearer|Basic)\s+[^\s,;\"\']+',
            r'(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|(?:client[_-])?secret|password|passwd)'
            r'["\']?\s*[=:]\s*(?:"[^"\n]*"|\'[^\'\n]*\'|[^\s,;]+)',
            r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----[\s\S]*?(?:-----END (?:[A-Z]+ )?PRIVATE KEY-----|\Z)',
            r'\bAIza[0-9A-Za-z_-]{20,}',
            r'\bsk-[0-9A-Za-z_-]{16,}',
            r'(?i)https?://[^\s/:]+:[^\s/@]+@',
        )
        for pattern in patterns:
            text = re.sub(pattern, '[REDACTED]', text)
        encoded = text.encode('utf-8')
        retained = encoded[:DIAGNOSTIC_LIMIT].decode('utf-8', errors='ignore').encode('utf-8')
        metadata.update(retained_bytes=len(retained), truncated=len(encoded) > DIAGNOSTIC_LIMIT,
                        redaction_status='known_patterns_applied' if text != original else 'no_known_patterns_detected')
        return metadata, retained
    except (UnicodeError, ValueError, TypeError, re.error):
        return metadata, None


_MESSAGES = {
    'invalid_contract': (
        'preflight', 'The plan or worker result did not satisfy its declared contract.',
        'Correct the contract issue described in the top-level detail, then validate the plan again.',
        'After review, resume this run with: ',
    ),
    'unsupported_platform': (
        'preflight', 'The runner requires Python 3.12 or later on macOS or Linux.',
        'Run the installed runner with a supported Python version and operating system.',
        'After review, resume this run with: ',
    ),
    'invalid_policy': (
        'preflight', 'The selected policy file could not be validated.',
        'Review the selected policy file and rerun doctor before another provider attempt.',
        'After review, resume this run with: ',
    ),
    'invalid_resume_state': (
        'recovery', 'The saved run state could not be validated.',
        'Inspect the saved run files and reconcile them before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'unsafe_state_path': (
        'recovery', 'The saved state path contains a symbolic link.',
        'Inspect the path and saved state; do not replace or delete files as a workaround.',
        'After review, resume this run with: ',
    ),
    'provider_version_failed': (
        'preflight', 'The configured Gemini executable did not complete its version check.',
        'Check the configured Gemini executable and supported version before another attempt.',
        'After review, resume this run with: ',
    ),
    'unsupported_gemini_version': (
        'preflight', 'The configured Gemini version is not supported by this runner.',
        'Select a supported Gemini CLI version and rerun doctor before another attempt.',
        'After review, resume this run with: ',
    ),
    'missing_skill_dependency': (
        'preflight', 'A required Gemini-visible skill file is missing or unreadable.',
        'Restore the required skill files through the normal setup process, then rerun doctor.',
        'After review, resume this run with: ',
    ),
    'policy_changed': (
        'preflight', 'The selected policy no longer matches the reviewed bytes recorded for this run.',
        'Review the policy bytes; if the change is intended, select them explicitly with --policy when resuming.',
        'After review, resume this run with: ',
    ),
    'worktree_locked': (
        'preflight', 'Another runner currently owns this worktree.',
        'Wait for the owning runner to finish and verify its status before retrying. Do not remove the lock manually.',
        'After review, resume this run with: ',
    ),
    'git_operation_in_progress': (
        'preflight', 'Git reports an operation in progress in this worktree.',
        'Finish or reconcile the existing Git operation yourself before continuing.',
        'After review, resume this run with: ',
    ),
    'dirty_worktree': (
        'preflight', 'A fresh run requires a clean index and worktree.',
        'Review and reconcile existing changes yourself; do not reset or discard them to proceed.',
        'After review, resume this run with: ',
    ),
    'unclean_execution_requires_reconciliation': (
        'recovery', 'A previous child process may still be active or its work may need reconciliation.',
        'Confirm the old process tree has stopped and inspect the task changes before acknowledging an unclean stop.',
        'After confirming cleanup and reviewing the work, resume with: ',
    ),
    'cleanup_unconfirmed': (
        'recovery', 'The runner could not confirm that every owned child process has stopped.',
        'Confirm owned child processes have stopped and inspect the saved worktree before any resume; do not start another provider while cleanup is uncertain.',
        'After confirming cleanup and reviewing the work, resume with: ',
    ),
    'worker_blocked': (
        'worker', 'The validated worker result is blocked.',
        'Review the blocked task and its recorded result before deciding whether to continue.',
        'After review, resume this run with: ',
    ),
    'worker_failed': (
        'worker', 'The worker reported that it could not complete the task.',
        'Review the task and saved worker result before deciding whether to continue.',
        'After review, resume this run with: ',
    ),
    'provider_blocked': (
        'provider', 'Gemini did not provide a usable result for this iteration.',
        'Inspect the saved provider diagnostic when present and the provider session through Gemini’s own interface. Pattern-based redaction cannot guarantee removal of arbitrary secrets; review diagnostic text before sharing it.',
        'After review, resume this run with: ',
    ),
    'diagnostic_persistence_failed': (
        'recovery', 'The sanitized provider diagnostic could not be persisted.',
        'Inspect the run directory and local filesystem state before deciding whether to resume.',
        'After review, resume this run with: ',
    ),
    'spawn_error': (
        'provider', 'The configured executable could not be started.',
        'Check the executable path and local process restrictions before another provider attempt.',
        'After review, resume this run with: ',
    ),
    'protocol': (
        'provider', 'The provider response did not satisfy the supported stream protocol.',
        'Inspect the saved provider session and runner diagnostics before deciding whether to resume.',
        'After review, resume this run with: ',
    ),
    'transient_infrastructure': (
        'provider', 'The provider reported a transient service condition.',
        'Review the saved attempt and provider status before deciding whether another attempt is appropriate.',
        'After review, resume this run with: ',
    ),
    'verification_blocked': (
        'verification', 'A verification command failed without an authorized repair policy.',
        'Review the saved verification log and declared failure policy before changing the plan or task inputs.',
        'After review, resume this run with: ',
    ),
    'verification_timeout': (
        'verification', 'A verification command exceeded its declared time limit.',
        'Review the verification log and determine whether the declared timeout and command are still appropriate.',
        'After review, resume this run with: ',
    ),
    'verification': (
        'verification', 'A verification command failed and its policy permits an implementation repair.',
        'Review the saved verification log and task diagnostics before continuing.',
        'After review, resume this run with: ',
    ),
    'commit_failed': (
        'recovery', 'The verified changes could not be committed.',
        'Preserve the staged work and inspect the saved transaction before resuming after a reviewed Git or hook fix.',
        'After review, resume this run with: ',
    ),
    'failure_limit': (
        'recovery', 'The runner stopped after three failures without verified progress.',
        'Inspect the saved attempts and diagnostics, then reconcile the plan and worktree before deciding whether to resume.',
        'After review, resume this run with: ',
    ),
    'total_deadline': (
        'recovery', 'The invocation reached its total runtime limit.',
        'Inspect the saved run and current worker state before deciding whether to resume with a new runtime budget.',
        'After review, resume this run with: ',
    ),
    'interrupted': (
        'recovery', 'The invocation was interrupted.',
        'Inspect the saved run and confirm any owned processes have stopped before deciding whether to resume.',
        'After review, resume this run with: ',
    ),
    'unexpected_branch': (
        'recovery', 'The worktree branch changed during execution.',
        'Inspect Git history and the saved run before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'unexpected_head': (
        'recovery', 'HEAD changed outside the runner’s verified commit transaction.',
        'Inspect Git history and reconcile the saved run before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'unexpected_index': (
        'recovery', 'The Git index changed outside the runner’s verified transaction.',
        'Inspect the index and saved run before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'unexpected_plan_change': (
        'recovery', 'The plan changed outside the runner’s transaction.',
        'Inspect the plan and saved transaction before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'out_of_scope_change': (
        'recovery', 'The worktree contains a change outside the current task scope.',
        'Inspect the changed files and reconcile them with the task’s authorized paths before continuing.',
        'After review, resume this run with: ',
    ),
    'submodule_change': (
        'recovery', 'The current task changed a Git submodule.',
        'Inspect the submodule state and reconcile it manually before attempting recovery.',
        'After review, resume this run with: ',
    ),
    'staged_content_mismatch': (
        'recovery', 'Staged bytes differ from the verified candidate.',
        'Inspect Git filters and staged content; do not commit until the verified bytes match.',
        'After review, resume this run with: ',
    ),
}

_UNKNOWN = (
    'recovery',
    'The runner could not map this reason to a trusted diagnostic.',
    'Inspect the report and local diagnostics to identify the cause. Do not infer authentication or permission state from an unknown reason.',
    'After review, resume this run with: ',
)


def _saved_run(directory):
    if directory is None:
        return None
    try:
        path = Path(directory).absolute()
        state = path / 'state.json'
        if path.is_symlink() or state.is_symlink() or not state.is_file():
            return None
        return path
    except (OSError, TypeError, ValueError):
        return None


def make_blocker(reason, *, task_id=None, run_directory=None, plan_path=None,
                 run_script=None, fallback_source='recovery'):
    """Build one bounded blocker using only runner-owned reason mappings."""
    code = reason if isinstance(reason, str) and reason else 'unknown_reason'
    source, detail, action, resume_prefix = _MESSAGES.get(code, _UNKNOWN)
    if code not in _MESSAGES:
        source = fallback_source

    saved = _saved_run(run_directory)
    remediation = [action]
    if saved is not None and plan_path is not None:
        script = Path(run_script or Path(__file__).with_name('run.py')).resolve()
        command = ' '.join(shlex.quote(value) for value in (
            'python3', str(script), str(Path(plan_path).resolve()), '--resume', str(saved)))
        instruction = resume_prefix + command
        if len(instruction) <= 4096:
            remediation.append(instruction)
        else:
            remediation.append('Resume the inspected saved run with its original plan after reviewing the state.')

    bounded = [item[:4096] for item in remediation[:32]]
    return dict(reason_code=code, source=source, task_id=task_id if isinstance(task_id, str) else None,
                detail=detail[:4096], remediation=bounded,
                resume=dict(required=saved is not None, run_directory=str(saved) if saved is not None else None))


def readiness_blockers(entries, *, run_directory=None, plan_path=None, run_script=None):
    """Translate local readiness findings to the shared summary blocker shape."""
    result = []
    for entry in entries[:128]:
        code = entry.get('reason_code') if isinstance(entry, dict) else None
        result.append(make_blocker(code, run_directory=run_directory, plan_path=plan_path,
                                   run_script=run_script, fallback_source='preflight'))
    return result
