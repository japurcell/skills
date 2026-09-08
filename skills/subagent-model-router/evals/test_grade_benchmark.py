import unittest

from grade_benchmark import grade


def decision(agent, tier, model, reason='bounded work', fallback='same-tier fallback'):
    return dict(applicable=True, agent_type=agent, model_tier=tier, model=model,
                justification=reason, fallback_strategy=fallback)


class RoutingGraderTests(unittest.TestCase):
    def passes(self, eval_id, value):
        return all(item['passed'] for item in grade(eval_id, value, ''))

    def test_current_fast_route(self):
        self.assertTrue(self.passes(0, decision('task', 'fast', 'gpt-5.6-luna')))
        self.assertTrue(self.passes(0, decision('task', 'fast', 'mai-code-1.1-flash')))

    def test_standard_model_cannot_masquerade_as_fast(self):
        self.assertFalse(self.passes(0, decision('task', 'fast', 'gpt-5.4-mini')))

    def test_unknown_model_cannot_pass_by_mentioning_code(self):
        self.assertFalse(self.passes(1, decision('general-purpose', 'standard', 'unknown', 'code refactor')))

    def test_editor_standard_route(self):
        self.assertTrue(self.passes(1, decision('editor', 'standard', 'gpt-5.6-terra')))

    def test_standard_review_fallback(self):
        self.assertTrue(self.passes(2, decision('code-reviewer', 'standard', 'gpt-5.4-mini')))
        self.assertFalse(self.passes(2, decision('code-reviewer', 'standard', 'gpt-5.6-terra')))

    def test_security_requires_premium_specialist_and_known_model(self):
        self.assertTrue(self.passes(5, decision('security-review', 'premium', 'gpt-5.6-sol', 'fresh routing: stakes changed')))
        for agent, tier, model in [('editor', 'premium', 'gpt-5.6-sol'),
                                   ('security-review', 'standard', 'gpt-5.3-codex'),
                                   ('security-review', 'premium', 'invented-model')]:
            self.assertFalse(self.passes(5, decision(agent, tier, model, 'fresh routing: stakes changed')))

    def test_missing_dependency_keeps_execution_fast(self):
        self.assertTrue(self.passes(7, decision('task', 'fast', 'gpt-5.6-luna', 'diagnose missing dependency')))
        self.assertFalse(self.passes(7, decision('task', 'premium', 'gpt-6-astra', 'diagnose missing dependency')))

    def test_bounded_review_preserves_standard_floor(self):
        self.assertTrue(self.passes(8, decision('code-reviewer', 'standard', 'gpt-5.4-mini')))
        self.assertFalse(self.passes(8, decision('code-reviewer', 'fast', 'gpt-5.6-luna')))

    def test_security_budget_allows_capable_cheapest_candidate(self):
        self.assertTrue(self.passes(9, decision('security-review', 'premium', 'gpt-5.6-sol', 'evaluated capable; lowest total cost')))
        self.assertFalse(self.passes(9, decision('security-review', 'standard', 'gpt-5.3-codex', 'cheaper')))


if __name__ == '__main__':
    unittest.main()
