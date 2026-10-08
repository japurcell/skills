"""Fixture-scoped structural checks; semantic task quality needs model review."""
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

BUNDLE = Path(__file__).parent
REPOSITORY = BUNDLE.parents[2]
UI_TERMS = r'\b(?:badges?|lists?|filters?|dropdowns?|controls?|modals?|forms?|pages?|cards?|rows?|buttons?|tables?|browser)\b'
BACKEND_UI_TERMS = (
    r'\b(?:ui|user interface|frontend|front[- ]end|screens?|badges?|dropdowns?|modals?|buttons?|browser|playwright(?:-cli)?)\b'
    r'|\b(?:display|render|show)\b[^.;\n]{0,80}\b(?:lists?|filters?|controls?|forms?|pages?|cards?|rows?|tables?)\b'
    r'|\b(?:lists?|filters?|controls?|forms?|pages?|cards?|rows?|tables?)\b[^.;\n]{0,80}\b(?:visible|displayed|rendered|on.screen)\b'
    r'|\b(?:settings|dashboard|web|login|signup|input|creation)\s+(?:pages?|forms?|cards?|controls?)\b'
)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, required=False):
    return isinstance(value, list) and (bool(value) or not required) and all(nonempty(x) for x in value)


def relative_path(value):
    if not nonempty(value) or '\x00' in value or PureWindowsPath(value).drive or '\\' in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and '..' not in path.parts


def referenced_section_exists(source, section):
    if not relative_path(source) or not nonempty(section):
        return False
    source_path = (REPOSITORY / source).resolve()
    if not source_path.is_relative_to(REPOSITORY.resolve()) or not source_path.is_file():
        return False
    headings = re.findall(r'^#+\s+(.+)$', source_path.read_text(errors='replace'), re.M)
    return section.lstrip('#').strip() in headings


def records(value):
    return [record for record in value if isinstance(record, dict)] if isinstance(value, list) else []


def content(task):
    return ' '.join(str(task.get(k, '')) for k in ('title', 'description', 'acceptanceCriteria')).lower()


SCENARIO_REQUIREMENTS = {
    0: ['stor|persist', 'status', 'chang|updat', 'list', 'card', 'badge', 'filter', 'pending', 'in.progress', 'done',
        'existing.*default.*pending|existing.*pending.*default', 'control|dropdown|select|inline'],
    1: ['invit', 'email', 'role', 'viewer', 'editor', 'admin', 'revok', 'access', 'audit', 'record|log', 'recent', 'review|view', 'settings'],
    2: ['persist', 'session', 'badge', 'list', 'mark', 'unread', 'filter', 'clear.*read|read.*clear', 'all'],
    3: ['hash', 'revokedat.*null', 'creat', 'label.*length|length.*label', 'plaintext.*once|once.*plaintext', 'without delet|not delet|retain.*revok'],
    4: ['interrupt', 'repeat', 'conflict', 'authority', 'metadata', 'owner.*approval', 'integration|shared.invariant'],
    5: ['retention', 'owner.*approval'],
}


def check_task_fields(task, index, schema):
    tid = task.get('id')
    if tid != f'T{index+1:03d}':
        schema.append(f'{tid}: expected T{index+1:03d}')
    if not all(nonempty(task.get(k)) for k in ('title', 'description')) or not strings(task.get('acceptanceCriteria'), True):
        schema.append(f'{tid}: title, description and acceptanceCriteria required')
    if not nonempty(task.get('parentStoryId')):
        schema.append(f'{tid}: parentStoryId required')
    paths = task.get('filesLikelyTouched')
    if not strings(paths) or not all(relative_path(path) for path in paths):
        schema.append(f'{tid}: filesLikelyTouched must contain repository-relative paths')
    guidance = task.get('designGuidance')
    if not isinstance(guidance, list) or not all(
        isinstance(entry, dict) and all(nonempty(entry.get(field)) for field in ('source', 'description', 'rationale'))
        for entry in guidance
    ):
        schema.append(f'{tid}: designGuidance records require source, description and rationale')
    if type(task.get('priority')) is not int:
        schema.append(f'{tid}: integer priority required')
    if task.get('passes') is not False or task.get('notes') != '':
        schema.append(f'{tid}: fresh defaults must be false/empty')
    if task.get('taskType') not in ('decision', 'implementation', 'verification', 'integration', 'documentation'):
        schema.append(f'{tid}: invalid taskType')


def check_dependencies(task, index, ids, errors):
    tid = task.get('id')
    schema = errors['Enriched schema']
    deps = task.get('dependsOn')
    if not strings(deps):
        schema.append(f'{tid}: dependsOn array required')
        deps = []
    if len(set(deps)) != len(deps):
        errors['Dependency graph'].append(f'{tid}: duplicate edges {deps}')
    for dep in deps:
        if dep not in ids or ids.index(dep) >= index:
            errors['Dependency graph'].append(f'{tid}: unknown/self/forward/cyclic edge {dep}')
    for dep in set(re.findall(r'\b(?:depends?\s+on|requires?|after)\s+(t\d{3})\b', content(task))):
        dep = dep.upper()
        if dep != tid and dep not in deps:
            errors['Explicit prerequisite'].append(f'{tid}: prose prerequisite {dep} absent from dependsOn')


def check_references(task, errors):
    tid = task.get('id')
    schema = errors['Enriched schema']
    for field, detail in (('sourceRefs', 'requirements'), ('requiredContext', 'purpose')):
        refs = task.get(field)
        if not isinstance(refs, list) or not all(isinstance(r, dict) for r in refs) or (field == 'sourceRefs' and not refs):
            schema.append(f'{tid}: invalid/missing {field}')
            continue
        for ref in refs:
            if not all(k in ref for k in ('path', 'section', detail)):
                errors['Source and context references'].append(f'{tid}: incomplete {field} reference')
            valid_detail = strings(ref.get(detail), True) if detail == 'requirements' else nonempty(ref.get(detail))
            if not valid_detail:
                errors['Source and context references'].append(f'{tid}: {detail} required')
            source, section = ref.get('path'), ref.get('section')
            if source is None and section is None:
                valid = nonempty(ref.get('content'))
            elif referenced_section_exists(source, section):
                valid = True
            else:
                valid = False
            if not valid:
                errors['Source and context references'].append(f'{tid}: unresolved {source}/{section} or missing inline content')


def check_verification(task, errors):
    tid = task.get('id')
    schema = errors['Enriched schema']
    checks = task.get('verification')
    if not isinstance(checks, list) or not checks or not all(isinstance(check, dict) for check in checks):
        schema.append(f'{tid}: verification records required')
        return
    check_ids = []
    for check in checks:
        check_id, kind, applicability = check.get('id'), check.get('kind'), check.get('applicability')
        if set(check) != {'id', 'kind', 'applicability', 'command', 'workingDirectory', 'expected', 'reason'}:
            schema.append(f'{tid}/{check_id}: check requires exactly the seven verification fields')
        if not nonempty(check_id) or check_id in check_ids:
            schema.append(f'{tid}/{check_id}: nonempty unique check ID required')
        check_ids.append(check_id)
        if kind not in ('test', 'typecheck', 'build', 'lint', 'manual') or applicability not in ('required', 'not-applicable', 'unresolved'):
            schema.append(f'{tid}/{check_id}: invalid check kind/applicability')
        if not relative_path(check.get('workingDirectory')) or not nonempty(check.get('expected')) or not nonempty(check.get('reason')):
            schema.append(f'{tid}/{check_id}: repository-relative workingDirectory and expected/reason strings required')
        command = check.get('command')
        if kind == 'manual' or applicability == 'not-applicable':
            valid_command = command is None
        elif applicability == 'required':
            valid_command = nonempty(command)
        else:
            valid_command = command is None or nonempty(command)
        if not valid_command:
            schema.append(f'{tid}/{check_id}: command must follow kind/applicability rules')
        if applicability == 'unresolved':
            errors['Verification readiness'].append(f'{tid}/{check_id}: unresolved {check.get("reason")}')
    if not any(check.get('kind') == 'typecheck' for check in checks):
        schema.append(f'{tid}: explicit typecheck applicability required')
    if not any(check.get('kind') in ('test', 'manual') and check.get('applicability') == 'required' for check in checks):
        schema.append(f'{tid}: required behavior check missing')


def check_scenario(eval_id, data, tasks, errors):
    blob = ' '.join(content(task) for task in tasks)
    if eval_id == 0:
        ui_tasks = [task for task in tasks if re.search(UI_TERMS, content(task))]
        if not ui_tasks:
            errors['UI browser verification'].append('No assigned UI behavior')
        for task in ui_tasks:
            checks = task.get('verification')
            checks = checks if isinstance(checks, list) else []
            if not any(isinstance(check, dict) and check.get('applicability') == 'required'
                       and check.get('kind') in ('test', 'manual')
                       and 'playwright-cli' in str(check.get('expected', '')).lower()
                       and 'browser' in str(check.get('expected', '')).lower()
                       for check in checks):
                errors['UI browser verification'].append(f'{task.get("id")}: required browser scenario using playwright-cli missing')
    if eval_id == 3:
        for task in tasks:
            checks = task.get('verification')
            check_text = str(checks).lower() if isinstance(checks, list) else ''
            if re.search(BACKEND_UI_TERMS, content(task)) or re.search(r'\bbrowser\b|playwright-cli', check_text):
                errors['Backend-only scope'].append(f'{task.get("id")}: invented UI/browser work')
    if eval_id == 1 and data.get('branchName') != 'workspace-member-management':
        errors['Feature branch'].append('branchName must derive from Workspace Member Management')
    if eval_id in (1, 2):
        horizontal_titles = ('build backend', 'build frontend', 'implement the feature',
                             'implement notification center', 'implement workspace member management',
                             'implement personal access token backend')
        for task in tasks:
            if any(title in str(task.get('title', '')).lower() for title in horizontal_titles):
                errors['Assignment boundaries'].append(f'{task.get("id")}: horizontal or umbrella title needs a bounded outcome')
    if eval_id == 4:
        if not any(task.get('taskType') == 'integration' for task in tasks):
            errors['Domain coverage'].append('Missing final integration assignment')
        for task in tasks:
            refs = [ref for field in ('sourceRefs', 'requiredContext')
                    for ref in records(task.get(field))]
            if not any(ref.get('section') == 'Current Contract' or re.search(r'active metadata.*authority', str(ref.get('content', '')).lower()) for ref in refs):
                errors['Source and context references'].append(f'{task.get("id")}: lifecycle current authority context missing')
    if eval_id not in SCENARIO_REQUIREMENTS:
        errors['Domain coverage'].append(f'Unsupported eval {eval_id}')
    for pattern in SCENARIO_REQUIREMENTS.get(eval_id, []):
        if not re.search(pattern, blob):
            errors['Domain coverage'].append(f'Missing assigned requirement: {pattern}')


def check_manifest(eval_id, run):
    path = run / 'outputs' / ('generated/tasks.json' if eval_id == 1 else 'tasks.json')
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {}
    data = data if isinstance(data, dict) else {}
    raw = data.get('tasks')
    tasks = raw if isinstance(raw, list) and all(isinstance(task, dict) for task in raw) else []
    labels = ('Enriched schema', 'Dependency graph', 'Source and context references',
              'Explicit prerequisite', 'Domain coverage', 'Verification readiness',
              'UI browser verification', 'Backend-only scope', 'Feature branch', 'Assignment boundaries')
    errors = {label: [] for label in labels}
    schema = errors['Enriched schema']
    if not tasks or not all(nonempty(data.get(field)) for field in ('project', 'branchName', 'description')):
        schema.append('Nonempty tasks and project/branchName/description required')
    ids = [task.get('id') for task in tasks]
    priorities = [task['priority'] for task in tasks if type(task.get('priority')) is int]
    for index, task in enumerate(tasks):
        check_task_fields(task, index, schema)
        check_dependencies(task, index, ids, errors)
        check_references(task, errors)
        check_verification(task, errors)
    if priorities != sorted(priorities) or len(set(priorities)) != len(priorities):
        schema.append('Priorities must be unique and ascending')
    check_scenario(eval_id, data, tasks, errors)
    return [{'text': label, 'passed': not failures, 'evidence': '; '.join(failures) or 'Checked'}
            for label, failures in errors.items()]
