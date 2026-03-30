Keep this as a single TDD regression slice and run only the narrow test target so the unrelated SMTP failure does not pollute the signal.

## 1. RED: add the regression test first

Add a focused test for the reported bug (in your existing email-normalization test file, or a new one like `tests/test_email_normalization.py`):

```python
from your_module import normalize_email


def test_normalize_email_strips_outer_whitespace_and_lowercases():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

Run only this test (not the full suite):

```bash
pytest -q tests/test_email_normalization.py::test_normalize_email_strips_outer_whitespace_and_lowercases
```

Expected RED failure (clean and relevant):

```text
E   AssertionError: assert '  alice@example.com  ' == 'alice@example.com'
```

## 2. GREEN: make the smallest fix

Update implementation minimally:

```python
def normalize_email(email):
    return email.strip().lower()
```

Re-run the same single test:

```bash
pytest -q tests/test_email_normalization.py::test_normalize_email_strips_outer_whitespace_and_lowercases
```

Expected GREEN:

```text
1 passed
```

## 3. REFACTOR: stop if no duplication/complexity

No refactor is needed here; `strip().lower()` is already the minimal clear fix for the bug.

If you want one extra confidence check without inviting unrelated failures, run only nearby normalization tests (for example, with `-k normalize_email`) and still avoid the full suite until the SMTP test is handled separately.
