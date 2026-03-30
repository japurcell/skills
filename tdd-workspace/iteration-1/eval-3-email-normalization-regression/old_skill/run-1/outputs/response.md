Keep the TDD loop focused on the regression so the unrelated SMTP failure does not pollute the signal. Run only the normalization test while you work on this bug.

Start with a regression test around the public behavior:

```python
from your_module import normalize_email


def test_normalize_email_trims_surrounding_whitespace_and_lowercases():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

Run only that test:

```bash
pytest tests/test_email_normalization.py::test_normalize_email_trims_surrounding_whitespace_and_lowercases -q
```

RED: with the current implementation, this should fail because `lower()` changes case but leaves the surrounding spaces intact.

Then make the smallest production change that satisfies the test:

```python
def normalize_email(email):
    return email.strip().lower()
```

Run the same focused test again:

```bash
pytest tests/test_email_normalization.py::test_normalize_email_trims_surrounding_whitespace_and_lowercases -q
```

GREEN: it should now pass.

Refactor: there is not much to clean up here; `strip().lower()` is already the minimal readable fix for the bug you described.

To keep the signal clean, do not use the full suite during this loop. The failure in `tests/test_notifications.py::test_sends_signup_email` is unrelated to email normalization, so it should be left out of this TDD cycle. After the regression test passes, you can optionally run just the containing test file or other normalization-specific tests, but avoid the full suite until the SMTP issue is handled separately.
