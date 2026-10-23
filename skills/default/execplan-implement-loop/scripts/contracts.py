"""Strict, versioned Markdown and worker contracts. No subprocess execution."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import TypedDict

LIMIT = 1024 * 1024
STATES = {'open', 'in_progress', 'verification_pending', 'commit_preparing', 'commit_pending', 'done'}
ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}\Z')
BLOCK = re.compile(r'^```execplan-loop-v1\n(.*?)^```[ \t]*$', re.M | re.S)
MARKER = re.compile(r'<!-- execplan-loop:generated ([A-Za-z0-9_-]+):(start|end) -->')


class Stop(Exception):
    def __init__(self, reason: str, detail: str = '', code: int = 2):
        super().__init__(detail or reason)
        self.reason, self.detail, self.code = reason, detail or reason, code


class WorkerResult(TypedDict):
    schema_version: int
    iteration_id: str
    task_id: str
    status: str
    summary: str
    changed_files: list[str]
    commit_message: str | None
    plan_notes: list[str]
    reason_code: str


def require(condition, message):
    if not condition:
        raise Stop('invalid_contract', message)


def object_keys(value, required, optional=()):
    require(isinstance(value, dict), 'Expected an object')
    require(set(required) <= value.keys() <= set(required) | set(optional),
            'Missing or unknown fields: ' + ', '.join(sorted(set(value) ^ set(required))))


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def decode(text):
    try:
        return json.loads(text, object_pairs_hook=no_duplicates,
                          parse_constant=lambda value: require(False, f'Nonfinite JSON: {value}'))
    except (ValueError, RecursionError) as error:
        raise Stop('invalid_contract', f'Invalid JSON: {error}') from error


def path_name(value, directory=False):
    require(isinstance(value, str) and value and '\x00' not in value and '\\' not in value,
            'Paths must be nonempty POSIX relative paths')
    plain = value.rstrip('/') if directory else value
    p = PurePosixPath(plain)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == plain,
            f'Unsafe or non-normalized path: {value}')
    require(not any(part.lower() == '.git' for part in p.parts), 'Git metadata is not writable scope')
    return value


def confined(root: Path, name: str):
    target = root / name
    require(target.resolve().is_relative_to(root.resolve()), f'Path escapes repository: {name}')
    return target


def positive(value):
    require(type(value) in (int, float) and math.isfinite(value) and value > 0,
            'Timeout must be a positive finite number')


def message_valid(message):
    require(isinstance(message, str) and len(message.encode()) <= 32768 and '\x00' not in message,
            'Invalid commit message')
    lines = message.splitlines()
    require(bool(lines) and len(lines[0]) <= 72 and not lines[0].endswith('.') and
            re.fullmatch(r'(docs|test|fix|feat|refactor|perf|chore)(\([A-Za-z0-9_./-]+\))?: \S.*', lines[0]),
            'Invalid commit subject')
    require(len(lines) > 2 and lines[1] == '', 'Commit body needs a blank line')
    for heading in ('Summary:', 'Rationale:', 'Tests:'):
        require(lines.count(heading) == 1, f'Commit message needs {heading}')
        i = lines.index(heading)
        require(i + 1 < len(lines) and lines[i + 1].startswith('- ') and lines[i + 1][2:].strip(),
                f'{heading} needs a bullet')
    require(lines.index('Summary:') < lines.index('Rationale:') < lines.index('Tests:'),
            'Commit sections out of order')
    require('Co-authored-by: Copilot' not in message, 'Copilot attribution explicitly declined')


def worker_result(text, iteration, task):
    require(len(text.encode()) <= LIMIT, 'Worker response exceeds 1 MiB')
    value = decode(text)
    object_keys(value, WorkerResult.__annotations__)
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unknown worker schema')
    require(value['iteration_id'] == iteration and value['task_id'] == task, 'Stale worker identity')
    require(value['status'] in ('ready_for_verification', 'blocked', 'failed'), 'Invalid worker status')
    for key in ('summary', 'reason_code'):
        require(isinstance(value[key], str) and 0 < len(value[key]) <= 4096, f'Invalid {key}')
    for key in ('changed_files', 'plan_notes'):
        require(isinstance(value[key], list) and len(value[key]) <= 10000 and
                all(isinstance(v, str) and len(v) <= 4096 for v in value[key]), f'Invalid {key}')
    require(len(set(value['changed_files'])) == len(value['changed_files']), 'Duplicate changed paths')
    for name in value['changed_files']:
        path_name(name)
    if value['status'] == 'ready_for_verification':
        message_valid(value['commit_message'])
    else:
        require(value['commit_message'] is None, 'Nonready result must have null commit_message')
    return value


class Plan:
    def __init__(self, path: Path, raw: bytes | None = None):
        self.path = path
        if raw is None:
            descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
            with os.fdopen(descriptor, 'rb') as source:
                require(stat.S_ISREG(os.fstat(source.fileno()).st_mode), 'Plan must be a regular file')
                raw = source.read(8 * LIMIT + 1)
        require(len(raw) <= 8 * LIMIT, 'Plan exceeds 8 MiB')
        try:
            self.text = raw.decode('utf-8')
        except UnicodeError as error:
            raise Stop('invalid_contract', 'Plan must be UTF-8') from error
        require('\r' not in self.text, 'Use LF newlines')
        blocks = list(BLOCK.finditer(self.text))
        require(len(blocks) == 1 and self.text.count('```execplan-loop-v1') == 1,
                'Expected exactly one execplan-loop-v1 block')
        self.block = blocks[0]
        self.data = decode(self.block[1])
        object_keys(self.data, ('schema_version', 'plan_id', 'tasks', 'milestones', 'final_task_id'))
        require(type(self.data['schema_version']) is int and self.data['schema_version'] == 1, 'Unknown plan schema')
        require(isinstance(self.data['plan_id'], str) and ID.fullmatch(self.data['plan_id']), 'Invalid plan_id')
        for key in ('tasks', 'milestones'):
            require(isinstance(self.data[key], list) and 0 < len(self.data[key]) <= 1000, f'Invalid {key}')
        self.tasks = {}
        for task in self.data['tasks']:
            object_keys(task, ('id', 'milestone_id', 'kind', 'depends_on', 'verification', 'writable_paths', 'state', 'evidence'))
            self.record(task, self.tasks)
            require(isinstance(task['milestone_id'], str), 'Invalid milestone_id')
            require(task['kind'] in ('implementation', 'verification'), 'Unknown task kind')
            require(isinstance(task['depends_on'], list) and all(isinstance(v, str) for v in task['depends_on']) and
                    len(task['depends_on']) == len(set(task['depends_on'])), 'Invalid prerequisites')
            require(isinstance(task['writable_paths'], list), 'Invalid writable_paths')
            for name in task['writable_paths']:
                path_name(name, directory=True)
                require(name != '.', 'Explicit files or directory prefixes required')
            require(isinstance(task['verification'], list) and task['verification'], 'Missing verification')
            commands = set()
            for check in task['verification']:
                object_keys(check, ('id', 'argv', 'cwd', 'timeout_seconds', 'expected_exit_code', 'failure_policy'))
                require(isinstance(check['id'], str) and ID.fullmatch(check['id']) and check['id'] not in commands, 'Invalid command ID')
                commands.add(check['id'])
                require(isinstance(check['argv'], list) and check['argv'] and
                        all(isinstance(a, str) and '\x00' not in a for a in check['argv']) and check['argv'][0], 'Invalid argv')
                path_name(check['cwd'])
                positive(check['timeout_seconds'])
                require(type(check['expected_exit_code']) is int and 0 <= check['expected_exit_code'] <= 255, 'Invalid expected exit')
                require(isinstance(check['failure_policy'], dict), 'Invalid failure_policy')
                for code, policy in check['failure_policy'].items():
                    require(re.fullmatch(r'(0|[1-9][0-9]*)', code) and 0 <= int(code) <= 255 and
                            int(code) != check['expected_exit_code'] and policy in ('repair', 'blocked'), 'Invalid failure mapping')
        self.milestones = {}
        for milestone in self.data['milestones']:
            object_keys(milestone, ('id', 'verification_task_id', 'state', 'evidence'))
            self.record(milestone, self.milestones)
        require(all(t['milestone_id'] in self.milestones for t in self.tasks.values()), 'Unknown milestone')
        self.ancestors = {}
        for task in self.tasks.values():
            require(set(task['depends_on']) <= self.tasks.keys(), 'Dangling prerequisite')
        remaining = dict(self.tasks)
        while remaining:
            ready = [identifier for identifier, task in remaining.items()
                     if set(task['depends_on']) <= self.ancestors.keys()]
            require(ready, 'Dependency cycle')
            for identifier in ready:
                parents = remaining.pop(identifier)['depends_on']
                self.ancestors[identifier] = set(parents).union(*(self.ancestors[p] for p in parents))
        for milestone in self.milestones.values():
            check = milestone['verification_task_id']
            require(isinstance(check, str) and check in self.tasks and self.tasks[check]['kind'] == 'verification' and
                    self.tasks[check]['milestone_id'] == milestone['id'], 'Invalid milestone verification task')
            required = {t['id'] for t in self.tasks.values() if t['milestone_id'] == milestone['id'] and t['kind'] == 'implementation'}
            require(required <= self.ancestors[check], 'Milestone does not depend on its implementation')
            require((milestone['state'] == 'done') == (self.tasks[check]['state'] == 'done'), 'Inconsistent milestone state')
        final = self.data['final_task_id']
        require(isinstance(final, str) and final in self.tasks and self.tasks[final]['kind'] == 'verification' and
                self.ancestors[final] == set(self.tasks) - {final}, 'Final check must depend on every task')
        for task in self.tasks.values():
            if task['state'] == 'done':
                require(all(self.tasks[p]['state'] == 'done' for p in task['depends_on']), 'Done task has unfinished prerequisite')
        names = {'progress', 'discoveries', 'decisions', 'outcomes'} | {'milestone-' + i for i in self.milestones}
        self.regions = {}
        active = None
        for match in MARKER.finditer(self.text):
            name, edge = match.groups()
            require(name in names, f'Unknown generated region: {name}')
            require(not (self.block.start() <= match.start() < self.block.end()), 'Region inside control block')
            if edge == 'start':
                require(active is None and name not in self.regions, 'Nested or duplicate generated region')
                active = (name, match.end())
            else:
                require(active is not None and active[0] == name, 'Unmatched generated region')
                self.regions[name] = (active[1], match.start())
                active = None
        require(active is None and set(self.regions) == names, 'Missing generated region')
        require(self.text.count('<!-- execplan-loop:generated') == len(names) * 2, 'Malformed generated marker')
        sections = {'progress': 'Progress', 'discoveries': 'Surprises & Discoveries',
                    'decisions': 'Decision Log', 'outcomes': 'Outcomes & Retrospective'}
        for title in ['Purpose / Big Picture', *sections.values()]:
            require(len(re.findall(r'^## ' + re.escape(title) + '$', self.text, re.M)) == 1,
                    f'Missing or duplicate section: {title}')
        for name, title in sections.items():
            prior = re.findall(r'^## (.+)$', self.text[:self.regions[name][0]], re.M)
            require(prior and prior[-1] == title, f'Generated {name} region is in the wrong section')
        for start, end in self.regions.values():
            require(not re.search(r'^#{1,6} ', self.text[start:end], re.M), 'Requirements headings cannot live in generated regions')
        for label, items in (('Task', self.tasks), ('Milestone', self.milestones)):
            hashes = '####' if label == 'Task' else '###'
            matches = re.findall(r'^' + hashes + r' ' + label + r' ([^ :]+): .+$', self.text, re.M)
            require(len(matches) == len(set(matches)) and set(matches) == set(items), f'Missing or duplicate {label} heading')
        for heading in re.finditer(r'^#### Task ([^ :]+): .+\n', self.text, re.M):
            rest = self.text[heading.end():]
            boundary = re.search(r'^#{1,4} ', rest, re.M)
            body = rest[:boundary.start()] if boundary else rest
            require(body.strip(), f'Empty task requirements: {heading[1]}')
        progress = self.text[slice(*self.regions['progress'])]
        entries = re.findall(r'^- \[([ x])\] \[([^]]+)\] ([^ :]+): .+$', progress, re.M)
        require(len(entries) == len(self.tasks) and {v[2] for v in entries} == set(self.tasks), 'Progress mapping mismatch')
        for mark, milestone, identifier in entries:
            task = self.tasks[identifier]
            require(milestone == task['milestone_id'] and (mark == 'x') == (task['state'] == 'done'), 'Inconsistent Progress state')
        for milestone in self.milestones.values():
            body = self.text[slice(*self.regions['milestone-' + milestone['id']])].strip()
            expected = 'Status: done\nAcceptance: met' if milestone['state'] == 'done' else 'Status: open\nAcceptance: not met'
            require(body == expected, 'Inconsistent milestone status')

    @staticmethod
    def record(record, mapping):
        identifier = record['id']
        require(isinstance(identifier, str) and ID.fullmatch(identifier) and identifier not in mapping, 'Duplicate or invalid ID')
        require(isinstance(record['state'], str) and record['state'] in STATES and isinstance(record['evidence'], list), 'Invalid state/evidence')
        for evidence in record['evidence']:
            object_keys(evidence, ('command_id', 'invocation_id', 'timestamp', 'exit_code', 'candidate_digest', 'log_reference'))
            require(type(evidence['exit_code']) is int and all(isinstance(evidence[k], str) for k in evidence if k != 'exit_code'), 'Invalid evidence')
        mapping[identifier] = record

    def immutable_hash(self):
        data = copy.deepcopy(self.data)
        for record in data['tasks'] + data['milestones']:
            del record['state'], record['evidence']
        parts = [(self.block.start(), self.block.end(), '<CONTROL>')]
        parts += [(start, end, '') for start, end in self.regions.values()]
        text = self.text
        for start, end, replacement in sorted(parts, reverse=True):
            text = text[:start] + replacement + text[end:]
        digest = hashlib.sha256()
        for part in (json.dumps(data, sort_keys=True, separators=(',', ':')).encode(), text.encode()):
            digest.update(len(part).to_bytes(8, 'big'))
            digest.update(part)
        return digest.hexdigest()

    def render(self, completed, evidence, notes=()):
        data = copy.deepcopy(self.data)
        for task in data['tasks']:
            if task['id'] in completed:
                task.update(state='done', evidence=evidence.get(task['id'], task['evidence']))
        for milestone in data['milestones']:
            if milestone['verification_task_id'] in completed:
                milestone.update(state='done', evidence=evidence.get(milestone['verification_task_id'], []))
        replacements = [(self.block.start(), self.block.end(), '```execplan-loop-v1\n' + json.dumps(data, indent=2) + '\n```')]
        bodies = {'progress': '\n'.join(f'- [{"x" if t["state"] == "done" else " "}] [{t["milestone_id"]}] {t["id"]}: Execute declared task' for t in data['tasks'])}
        safe_notes = [' '.join(note.split()).replace('<!--', '&lt;!--').replace('```', '` ` `') for note in list(notes)[-100:]]
        bodies['discoveries'] = '\n'.join('- ' + note for note in safe_notes) or 'No worker discoveries reported.'
        bodies['decisions'] = 'Declared verification commands gate runner-owned commits. Frozen requirements remain authoritative.'
        bodies['outcomes'] = f'Tasks recorded complete: {len(completed)} / {len(self.tasks)}. Consult the run journal for commit evidence.'
        for m in data['milestones']:
            bodies['milestone-' + m['id']] = 'Status: done\nAcceptance: met' if m['state'] == 'done' else 'Status: open\nAcceptance: not met'
        for name, body in bodies.items():
            start, end = self.regions[name]
            replacements.append((start, end, '\n' + body + '\n'))
        text = self.text
        for start, end, replacement in sorted(replacements, reverse=True):
            text = text[:start] + replacement + text[end:]
        result = text.encode()
        require(Plan(self.path, result).immutable_hash() == self.immutable_hash(), 'Rendering changed frozen requirements')
        return result
