"""Exercise the grader CLI, including its actual grading.json assertions."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

GRADER = Path(__file__).with_name('grade_benchmark.py')


def manifest():
    # Synthetic command records exercise schema rules, not product execution or tooling discovery.
    tasks = []
    criteria = ['Hashed token storage; revokedAt defaults null',
                'Create token validates label length; returns plaintext token once',
                'Revoke token marks revoked without deleting']
    for i, criterion in enumerate(criteria, 1):
        tasks.append(dict(id=f'T{i:03d}', parentStoryId=f'US-{i:03d}',
                          title=criterion, description=criterion,
                          acceptanceCriteria=[criterion], priority=i, passes=False,
                          filesLikelyTouched=[], designGuidance=[],
                          notes='', dependsOn=[] if i == 1 else ['T001'],
                          sourceRefs=[dict(path=None, section=None, content=criterion,
                                           requirements=[criterion])], requiredContext=[],
                          taskType='implementation', verification=[
                              dict(id='behavior', kind='test', applicability='required',
                                   command='python3 -m unittest', workingDirectory='.',
                                   expected='Token behavior checks pass', reason='Verify token behavior'),
                              dict(id='types', kind='typecheck', applicability='required',
                                   command='python3 -m mypy src', workingDirectory='.',
                                   expected='No type errors', reason='Hypothetical typechecker record for the synthetic CLI fixture')]))
    return dict(project='tokens', branchName='personal-access-token-backend',
                description='Token backend', tasks=tasks)


class GraderCliTests(unittest.TestCase):
    def test_verification_commands_follow_applicability(self):
        for kind, applicability, command in (
            ('manual', 'unresolved', 'python3 test.py'),
            ('typecheck', 'not-applicable', 'python3 test.py'),
            ('test', 'unresolved', ''), ('test', 'unresolved', 7),
        ):
            with self.subTest(kind=kind, applicability=applicability, command=command):
                data = manifest()
                check = dict(data['tasks'][0]['verification'][0])
                check.update(id='extra', kind=kind, applicability=applicability, command=command)
                data['tasks'][0]['verification'].append(check)
                self.assert_failed(data, 'Enriched schema')

    def test_original_fields_reject_malformed_values(self):
        for field, value in (
            ('parentStoryId', None), ('parentStoryId', []),
            ('filesLikelyTouched', None), ('filesLikelyTouched', ['../outside']),
            ('filesLikelyTouched', ['C:/outside']), ('designGuidance', None),
            ('designGuidance', [None]), ('designGuidance', [{'source': 'source'}]),
        ):
            with self.subTest(field=field, value=value):
                data = manifest()
                data['tasks'][0][field] = value
                self.assert_failed(data, 'Enriched schema')

    def test_repository_relative_source_and_context_resolve(self):
        data = manifest()
        for task in data['tasks']:
            task['sourceRefs'] = [dict(path='skills/spec-to-tasks/evals/files/lifecycle-prd.md',
                                      section='Current Contract', requirements=['Recovery authority'])]
            task['requiredContext'] = [dict(path='skills/spec-to-tasks/references/task-schema.md',
                                           section='Task types', purpose='Choose the task outcome')]
            task['filesLikelyTouched'] = ['src/tokens.py', 'tests/test_tokens.py']
            task['designGuidance'] = [dict(source='Current Contract', description='Preserve authority',
                                          rationale='Recovery must use current metadata')]
        self.assertEqual(self.grade(data)['summary']['failed'], 0)

    def test_reference_paths_and_malformed_values_are_rejected(self):
        for field, detail in (('sourceRefs', {'requirements': ['storage']}),
                              ('requiredContext', {'purpose': 'Current authority'})):
            for path in ('/tmp/source.md', '../outside.md', 'C:/private.md',
                         'C:\\private.md', 'evals/files/lifecycle-prd.md', {}, []):
                with self.subTest(field=field, path=path):
                    data = manifest()
                    data['tasks'][0][field] = [dict(path=path, section='Current Contract', **detail)]
                    self.assert_failed(data, 'Source and context references')

    def test_prerequisite_wording_variations_and_neutral_mentions(self):
        for description in ('Depends on T001.', 'Runs after T001 passes.', 'Requires T001 first.'):
            data = manifest()
            data['tasks'][1].update(description=description, dependsOn=[])
            self.assert_failed(data, 'Explicit prerequisite')
        for description in ('T003 consumes this task.', 'T003 verifies the result.',
                            'Compare this output with T003.', 'T003 depends on this task.'):
            data = manifest()
            data['tasks'][0]['description'] += ' ' + description
            self.assertEqual(self.grade(data)['summary']['failed'], 0)

    def test_existing_fields_and_check_value_rules(self):
        for field in ('parentStoryId', 'filesLikelyTouched', 'designGuidance'):
            data = manifest()
            data['tasks'][0].pop(field, None)
            self.assert_failed(data, 'Enriched schema')
        for field, value in (('reason', None), ('expected', None), ('workingDirectory', None),
                             ('workingDirectory', '/tmp'), ('workingDirectory', '../outside'),
                             ('workingDirectory', 'C:\\private')):
            data = manifest()
            data['tasks'][0]['verification'][0][field] = value
            self.assert_failed(data, 'Enriched schema')

    def test_lifecycle_malformed_references_do_not_crash(self):
        for value in (None, {}, [None]):
            data = manifest()
            data['tasks'][0]['requiredContext'] = value
            self.assert_failed(data, 'Enriched schema', 4)

    def test_downstream_id_mention_is_not_prerequisite(self):
        data = manifest()
        data['tasks'][0]['description'] += ' T003 consumes this task.'
        self.assertEqual(self.grade(data)['summary']['failed'], 0)

    def grade(self, data, eval_id=3, timing_text=None):
        return self.grade_output(json.dumps(data), eval_id, timing_text)

    def grade_output(self, output_text, eval_id=3, timing_text=None):
        with tempfile.TemporaryDirectory() as tmp:
            iteration = Path(tmp)/'iteration-1'
            run = iteration/f'eval-{eval_id}'/'with_skill'/'run-1'
            (run/'outputs').mkdir(parents=True)
            (run.parents[1]/'eval_metadata.json').write_text(json.dumps({'eval_id': eval_id}))
            output = run/'outputs'/('generated/tasks.json' if eval_id == 1 else 'tasks.json')
            output.parent.mkdir(parents=True, exist_ok=True)
            if output_text is not None:
                output.write_text(output_text)
            if timing_text is not None:
                (run/'timing.json').write_text(timing_text)
            result = subprocess.run(['python3', str(GRADER), str(iteration)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads((run/'grading.json').read_text())

    def test_unusable_artifacts_receive_no_credit_for_applicable_checks(self):
        totals = {0: 7, 1: 8, 2: 7, 3: 7, 4: 6, 5: 6}
        artifacts = (None, '', '{invalid', 'null', '[]', '{}',
                     '{"tasks": []}', '{"tasks": [null]}', '{"tasks": [{}]}')
        for eval_id, total in totals.items():
            for output_text in artifacts:
                with self.subTest(eval_id=eval_id, output_text=output_text):
                    grading = self.grade_output(output_text, eval_id)
                    self.assertEqual(grading['summary']['passed'], 0, grading['summary'])
                    self.assertEqual(grading['summary']['total'], total)
                    for expectation in grading['expectations']:
                        self.assertFalse(expectation['passed'], expectation)

    def assert_failed(self, data, term, eval_id=3):
        failures = [x for x in self.grade(data, eval_id)['expectations'] if not x['passed']]
        self.assertTrue(any(term in x['text'] for x in failures), failures)

    def test_complete_enriched_tasks_are_accepted(self):
        self.assertEqual(self.grade(manifest())['summary']['failed'], 0)

    def test_inspectable_incomplete_output_preserves_partial_credit(self):
        data = manifest()
        del data['tasks'][0]['parentStoryId']
        grading = self.grade(data)
        self.assertEqual(grading['summary'], dict(passed=6, failed=1, total=7, pass_rate=0.86))
        self.assertFalse(next(x for x in grading['expectations'] if x['text'] == 'Enriched schema')['passed'])

    def test_inspectable_tasks_need_inputs_for_each_credited_check(self):
        fields = {'dependsOn': ('Dependency graph', 'Explicit prerequisite'),
                  'sourceRefs': ('Source and context references',),
                  'requiredContext': ('Source and context references',),
                  'verification': ('Verification readiness',)}
        for field, categories in fields.items():
            for value in ('missing', None, {}, [None], [{}]):
                with self.subTest(field=field, value=value):
                    data = manifest()
                    task = data['tasks'][0]
                    if value == 'missing':
                        del task[field]
                    else:
                        task[field] = value
                    expectations = {x['text']: x for x in self.grade(data)['expectations']}
                    for category in categories:
                        self.assertFalse(expectations[category]['passed'], expectations[category])

        data = manifest()
        for task in data['tasks']:
            for field in fields:
                del task[field]
        grading = self.grade(data)
        self.assertEqual(grading['summary'], dict(passed=2, failed=5, total=7, pass_rate=0.29))

    def test_supported_required_check_kinds_are_structurally_accepted(self):
        for kind in ('test', 'typecheck', 'build', 'lint', 'manual'):
            with self.subTest(kind=kind):
                data = manifest()
                data['tasks'] = [data['tasks'][0]]
                task = data['tasks'][0]
                criterion = 'Verify retention and owner approval policy'
                task.update(title=criterion, description=criterion,
                            acceptanceCriteria=[criterion], taskType='verification')
                task['sourceRefs'][0].update(content=criterion, requirements=[criterion])
                task['verification'] = [dict(id='outcome', kind=kind, applicability='required',
                    command=None if kind == 'manual' else 'python3 verify_policy.py',
                    workingDirectory='.', expected='Retention and owner approval policy is verified',
                    reason='Directly establishes the assigned policy outcome')]
                if kind != 'typecheck':
                    task['verification'].append(dict(id='types', kind='typecheck',
                        applicability='not-applicable', command=None, workingDirectory='.',
                        expected='No typed source is in scope', reason='Policy verification only'))
                grading = self.grade(data, 5)
                self.assertEqual(grading['summary']['failed'], 0, grading['expectations'])
                self.assertEqual(grading['summary']['total'], 6)

    def test_existing_domain_requirements_remain_covered(self):
        cases = {
            0: 'Store status for each task, existing tasks default pending; change status using inline controls from task list; cards show badges; filter by pending, in progress and done.',
            1: 'Admins invite by email, change role between viewer editor admin, revoke workspace access, record membership changes in audit log, review recent changes in settings.',
            2: 'Persist notification read state across sessions, unread badges and notification list, mark read or unread, filter by read state, clear all read notifications.',
        }
        for eval_id, criterion in cases.items():
            with self.subTest(eval_id=eval_id):
                data = manifest()
                data['tasks'] = [data['tasks'][0]]
                task = data['tasks'][0]
                task.update(title='Bounded outcome', description=criterion, acceptanceCriteria=[criterion])
                task['sourceRefs'][0].update(content=criterion, requirements=[criterion])
                if eval_id == 0:
                    task['verification'].append(dict(id='browser', kind='manual', applicability='required', command=None,
                        workingDirectory='.', expected='Procedure: in browser using playwright-cli skill change a task status; evidence: card badge and filter update.',
                        reason='Verify visible task status behavior'))
                if eval_id == 1:
                    data['branchName'] = 'workspace-member-management'
                self.assertEqual(self.grade(data, eval_id)['summary']['failed'], 0)
                task.update(description='Basic feature works', acceptanceCriteria=['Basic feature works'])
                self.assert_failed(data, 'Domain coverage', eval_id)

    def test_ui_browser_check_is_required_and_accepts_concrete_wording(self):
        data = manifest()
        task = data['tasks'][0]
        criterion = 'Store status for each task; existing tasks default pending; change status from task list with inline controls; cards show badges; filter pending, in progress and done.'
        task.update(title='Task statuses', description=criterion, acceptanceCriteria=[criterion])
        self.assert_failed(data, 'UI browser verification', 0)
        task['verification'].append(dict(id='browser', kind='manual', applicability='required', command=None,
            workingDirectory='.', expected='Use the playwright-cli skill in a browser: change status from pending to done and observe the badge and filtered list.',
            reason='Confirm visible behavior'))
        self.assertEqual(self.grade(data, 0)['summary']['failed'], 0)

    def test_backend_only_scope_excludes_ui_and_browser_checks(self):
        data = manifest()
        data['tasks'][0]['acceptanceCriteria'].append('Show the token in a modal')
        self.assert_failed(data, 'Backend-only scope')
        data = manifest()
        data['tasks'][0]['verification'][0]['expected'] += '; verify in browser using playwright-cli skill'
        self.assert_failed(data, 'Backend-only scope')
        data = manifest()
        data['tasks'][0]['description'] += ' Use the token format contract.'
        self.assertEqual(self.grade(data)['summary']['failed'], 0)

    def test_backend_storage_and_collection_vocabulary_is_accepted(self):
        data = manifest()
        data['tasks'][0]['acceptanceCriteria'].append(
            'Store hashed tokens in a database table; revoke retains the row. '
            'Query filters omit revoked rows from token lists; preserve access controls.')
        self.assertEqual(self.grade(data)['summary']['failed'], 0)

    def test_backend_only_scope_still_rejects_explicit_ui_semantics(self):
        for criterion in ('Show the token in a modal', 'Add a token creation form',
                          'Show the token list in settings', 'Render token rows in a table',
                          'The token list is visible', 'Add controls to the settings page',
                          'Display revoked tokens on cards', 'Filter tokens in the browser',
                          'Add a revoke button', 'Add a token dropdown', 'Create a frontend'):
            with self.subTest(criterion=criterion):
                data = manifest()
                data['tasks'][0]['acceptanceCriteria'].append(criterion)
                self.assert_failed(data, 'Backend-only scope')

    def test_nul_source_and_context_paths_fail_without_crashing(self):
        for field, detail in (('sourceRefs', {'requirements': ['storage']}),
                              ('requiredContext', {'purpose': 'Current authority'})):
            with self.subTest(field=field):
                data = manifest()
                data['tasks'][0][field] = [dict(path='invalid\x00source.md',
                    section='Current Contract', **detail)]
                self.assert_failed(data, 'Source and context references')

    def test_nonobject_timing_is_unavailable_without_crashing(self):
        for value in (None, [], 'unexpected', 7, True):
            with self.subTest(value=value):
                grading = self.grade(manifest(), timing_text=json.dumps(value))
                self.assertEqual(grading['summary']['failed'], 0)
                self.assertIsNone(grading['timing']['total_duration_seconds'])
                self.assertIsNone(grading['timing']['executor_duration_seconds'])

    def test_object_and_invalid_json_timing_preserve_metric_contract(self):
        grading = self.grade(manifest(), timing_text='{"total_duration_seconds": 1.25}')
        self.assertEqual(grading['timing']['total_duration_seconds'], 1.25)
        self.assertEqual(grading['timing']['executor_duration_seconds'], 1.25)
        grading = self.grade(manifest(), timing_text='{invalid')
        self.assertIsNone(grading['timing']['total_duration_seconds'])

    def test_membership_branch_and_horizontal_title_rules_remain(self):
        data = manifest()
        self.assert_failed(data, 'Feature branch', 1)
        for eval_id, title in ((1, 'Build backend'), (1, 'Build frontend'),
                               (2, 'Implement notification center')):
            data = manifest()
            data['tasks'][0]['title'] = title
            self.assert_failed(data, 'Assignment boundaries', eval_id)

    def test_invalid_dependencies(self):
        for deps in (['T999'], ['T002'], ['T001', 'T001']):
            with self.subTest(deps=deps):
                data = manifest()
                data['tasks'][1]['dependsOn'] = deps
                self.assert_failed(data, 'Dependency graph')
        data = manifest()
        data['tasks'][0]['dependsOn'] = ['T003']
        self.assert_failed(data, 'Dependency graph')

    def test_partial_enrichment_is_rejected(self):
        data = manifest()
        del data['tasks'][0]['verification']
        self.assert_failed(data, 'Enriched schema')

    def test_generated_legacy_or_malformed_existing_fields_are_rejected(self):
        data = manifest()
        for task in data['tasks']:
            for field in ('sourceRefs', 'requiredContext', 'taskType', 'verification'):
                del task[field]
        self.assert_failed(data, 'Enriched schema')
        for field, value in (('priority', True), ('acceptanceCriteria', 'All tests pass'),
                             ('dependsOn', 'T001'), ('notes', None)):
            with self.subTest(field=field):
                data = manifest()
                data['tasks'][0][field] = value
                self.assert_failed(data, 'Enriched schema')

    def test_invented_reference_or_missing_inline_content(self):
        for ref in (dict(path='invented.md', section='Requirements', requirements=['storage']),
                    dict(path=None, section=None, requirements=['storage'])):
            data = manifest()
            data['tasks'][0]['sourceRefs'] = [ref]
            self.assert_failed(data, 'Source and context references')

    def test_unresolved_checks_do_not_count_as_ready(self):
        data = manifest()
        data['tasks'][0]['verification'][1].update(applicability='unresolved', command=None, reason='Tooling not supplied')
        self.assert_failed(data, 'Verification readiness')

    def test_known_command_can_be_retained_while_host_is_unresolved(self):
        data = manifest()
        data['tasks'][0]['verification'][1].update(applicability='unresolved', reason='Known command requires unavailable host')
        grading = self.grade(data)
        self.assertTrue(next(x for x in grading['expectations'] if x['text'] == 'Enriched schema')['passed'])
        self.assert_failed(data, 'Verification readiness')

    def test_duplicate_check_ids_and_missing_typecheck_classification(self):
        data = manifest()
        data['tasks'][0]['verification'][1]['id'] = 'behavior'
        self.assert_failed(data, 'Enriched schema')
        data = manifest()
        data['tasks'][0]['verification'] = data['tasks'][0]['verification'][:1]
        self.assert_failed(data, 'Enriched schema')
        data = manifest()
        data['tasks'][0]['verification'][0]['passed'] = True
        self.assert_failed(data, 'Enriched schema')

    def test_negative_behavior_cannot_be_dropped(self):
        data = manifest()
        task = data['tasks'][2]
        task.update(title='Revoke token', description='Token is revoked', acceptanceCriteria=['Token is revoked'])
        task['sourceRefs'][0]['requirements'] = ['Token is revoked']
        self.assert_failed(data, 'Domain coverage')

    def test_explicit_prerequisite_must_be_structured(self):
        data = manifest()
        data['tasks'][1]['description'] += ' Requires T001 first.'
        data['tasks'][1]['dependsOn'] = []
        self.assert_failed(data, 'Explicit prerequisite')

    def test_manual_docs_check_and_justified_typecheck(self):
        data = manifest()
        data['tasks'] = [data['tasks'][0]]
        task = data['tasks'][0]
        criterion = 'Document retention and owner approval'
        task.update(title=criterion, description=criterion, taskType='documentation', acceptanceCriteria=[criterion])
        task['sourceRefs'][0].update(content=criterion, requirements=[criterion])
        task['verification'] = [dict(id='review', kind='manual', applicability='required', command=None,
                                    workingDirectory='.', expected='Read the document and record evidence of retention and owner approval.', reason='Verify document accuracy'),
                                dict(id='types', kind='typecheck', applicability='not-applicable', command=None,
                                     workingDirectory='.', expected='No typed source is in scope', reason='Documentation only; no typed source changes.')]
        self.assertEqual(self.grade(data, 5)['summary']['failed'], 0)

    def test_lifecycle_requires_current_authority_and_integration_assignment(self):
        data = manifest()
        data['tasks'] = [data['tasks'][0]]
        task = data['tasks'][0]
        criterion = 'Interruption and repeated recovery preserve metadata authority; conflict refusal and owner approval have final integration proof.'
        task.update(title='Lifecycle integration', description=criterion, acceptanceCriteria=[criterion], taskType='integration')
        task['sourceRefs'] = [dict(path='skills/spec-to-tasks/evals/files/lifecycle-prd.md', section='Current Contract', requirements=[criterion])]
        self.assertEqual(self.grade(data, 4)['summary']['failed'], 0)
        task['sourceRefs'][0]['section'] = 'Requirements'
        self.assert_failed(data, 'Source and context references', 4)
        task['sourceRefs'][0]['section'] = 'Current Contract'
        task['taskType'] = 'implementation'
        self.assert_failed(data, 'Domain coverage', 4)

    def test_invalid_json_and_nonobject_tasks_fail_without_crashing(self):
        for eval_id in range(6):
            for data in (None, [], {'tasks':[None]}, {'tasks':[]}):
                with self.subTest(data=data, eval_id=eval_id):
                    self.assert_failed(data, 'Enriched schema', eval_id)

    def test_verification_values_are_valid_for_manual_and_inapplicable_checks(self):
        for applicability in ('required', 'not-applicable', 'unresolved'):
            for field in ('workingDirectory', 'expected', 'reason'):
                data = manifest()
                check = dict(data['tasks'][0]['verification'][0])
                check.update(id='manual', kind='manual', applicability=applicability, command=None)
                check[field] = None
                data['tasks'][0]['verification'].append(check)
                with self.subTest(applicability=applicability, field=field):
                    self.assert_failed(data, 'Enriched schema')

    def test_malformed_nested_records_fail_without_crashing(self):
        for field in ('sourceRefs', 'requiredContext', 'verification'):
            for value in (None, {}, [None], [[]], [7]):
                data = manifest()
                data['tasks'][0][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_failed(data, 'Enriched schema', 4)

    def test_status_default_and_controls_remain_required(self):
        criterion = 'Store status for each task, existing tasks default pending; change status using inline controls from task list; cards show badges; filter by pending, in progress and done.'
        for omitted in ('existing tasks default pending; ', 'using inline controls '):
            data = manifest()
            data['tasks'][0].update(description=criterion.replace(omitted, ''),
                                    acceptanceCriteria=[criterion.replace(omitted, '')])
            self.assert_failed(data, 'Domain coverage', 0)

    def test_false_fresh_defaults_or_missing_required_check(self):
        data = manifest()
        data['tasks'][0]['passes'] = True
        self.assert_failed(data, 'Enriched schema')
        data = manifest()
        data['tasks'][0]['verification'] = data['tasks'][0]['verification'][1:]
        data['tasks'][0]['verification'][0].update(applicability='not-applicable', command=None)
        self.assert_failed(data, 'Enriched schema')


if __name__ == '__main__':
    unittest.main()
