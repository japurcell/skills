import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PublicGraderTests(unittest.TestCase):
    def grade(self, eval_id, result, response, timing=None, metrics=None, full=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            case = root / 'eval-case'
            run = case / 'with_skill' / 'run-1'
            outputs = run / 'outputs'
            outputs.mkdir(parents=True)
            (case / 'eval_metadata.json').write_text(json.dumps({'eval_id': eval_id}))
            (outputs / 'decision.json').write_text(json.dumps(result))
            (outputs / 'decision.md').write_text(response)
            if timing is not None:
                (run / 'timing.json').write_text(json.dumps(timing))
            if metrics is not None:
                (run / 'metrics.json').write_text(json.dumps(metrics))
            cli = Path(__file__).with_name('grade_benchmark.py')
            completed = subprocess.run([sys.executable, str(cli), str(root)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            grading = json.loads((run / 'grading.json').read_text())
            return grading if full else grading['summary']['failed']

    def test_unavailable_metrics_stay_null_and_supplied_values_survive(self):
        result = {'status': 'complete', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        absent = self.grade(0, result, '<promise>COMPLETE</promise>', full=True)
        self.assertIsNone(absent['timing']['executor_duration_seconds'])
        self.assertIsNone(absent['execution_metrics']['total_tool_calls'])
        supplied = self.grade(0, result, '<promise>COMPLETE</promise>', timing={'total_duration_seconds': 2.5}, metrics={'total_tool_calls': 4}, full=True)
        self.assertEqual(supplied['timing']['executor_duration_seconds'], 2.5)
        self.assertEqual(supplied['execution_metrics']['total_tool_calls'], 4)

    def test_nonobject_output_is_failed_without_crash(self):
        self.assertGreater(self.grade(0, 7, '<promise>COMPLETE</promise>'), 0)

    def test_blocker_accepts_alternate_stop_wording(self):
        result = {'status': 'blocked', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        self.assertEqual(self.grade(3, result, '<promise>BLOCKED</promise>\nRequired browser host is unavailable; restore access. Halt until access returns.'), 0)

    def test_complete_protocol_must_be_exact(self):
        result = {'status': 'complete', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        self.assertEqual(self.grade(0, result, '<promise>COMPLETE</promise>'), 0)
        self.assertGreater(self.grade(0, result, 'Still blocked. <promise>COMPLETE</promise>'), 0)

    def test_task_complete_continues_without_manifest_selection(self):
        result = {'status': 'looping', 'next_action': 'spawn fresh worker', 'target_task_id': None, 'routing_decision': 'delegate-to-subagents'}
        self.assertEqual(self.grade(1, result, '<promise>TASK_COMPLETE</promise>\nUS-002 passed; dispatch a fresh prd-ralph worker without reading manifest or progress.'), 0)
        result['target_task_id'] = 'US-003'
        self.assertGreater(self.grade(1, result, 'Read prd.json to choose US-003.'), 0)

    def test_blocked_stops_and_preserves_actionable_reason(self):
        result = {'status': 'blocked', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        self.assertEqual(self.grade(3, result, '<promise>BLOCKED</promise>\nRequired browser host is unavailable; restore access. Stop without retry.'), 0)
        self.assertGreater(self.grade(3, result, '<promise>BLOCKED</promise>\nRetry worker again.'), 0)

    def test_invalid_worker_intake_stops_without_routing(self):
        result = {'status': 'blocked', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        self.assertEqual(self.grade(2, result, '<promise>BLOCKED</promise>\nInvalid manifest: tasks is missing. Supply a valid nonempty task array.'), 0)
        result['routing_decision'] = 'spawn retry'
        self.assertGreater(self.grade(2, result, '<promise>BLOCKED</promise>\nInvalid tasks; spawn retry.'), 0)

    def test_blocked_result_rejects_contradictory_routing(self):
        result = {'status': 'blocked', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': 'spawn retry'}
        response = '<promise>BLOCKED</promise>\nRequired browser host is unavailable; restore access. Stop without retry.'
        self.assertGreater(self.grade(3, result, response), 0)

    def test_decisions_require_complete_consistent_protocol_fields(self):
        complete = {'status': 'complete', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': None}
        for field in complete:
            result = dict(complete)
            del result[field]
            with self.subTest(missing=field):
                self.assertGreater(self.grade(0, result, '<promise>COMPLETE</promise>'), 0)
        for field, value in (('next_action', 'spawn retry'), ('routing_decision', 'delegate')):
            result = dict(complete, **{field: value})
            with self.subTest(field=field):
                self.assertGreater(self.grade(0, result, '<promise>COMPLETE</promise>'), 0)
        looping = {'status': 'looping', 'next_action': 'stop', 'target_task_id': None, 'routing_decision': 'delegate-to-subagents'}
        self.assertGreater(self.grade(1, looping, '<promise>TASK_COMPLETE</promise>\nDispatch a fresh prd-ralph worker.'), 0)

    def test_enriched_dispatch_forwards_constraints(self):
        result = {'status': 'looping', 'next_action': 'spawn fresh worker', 'target_task_id': None, 'routing_decision': 'delegate-to-subagents'}
        good = 'Dispatch fresh prd-ralph worker with prd_file=tasks.json progress_file=audit.txt commit=false. Preserve docs-only scope and stop before owner approval. Do not read manifest or progress.'
        self.assertEqual(self.grade(4, result, good), 0)
        self.assertGreater(self.grade(4, result, 'Dispatch prd-ralph worker.'), 0)


if __name__ == '__main__':
    unittest.main()
