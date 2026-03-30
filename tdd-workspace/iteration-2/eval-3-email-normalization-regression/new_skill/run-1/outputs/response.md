Let's keep this to one regression slice through the public function `normalize_email(email)` and avoid the noisy unrelated failure by not running the full suite.

## Cycle 1: reproduce the bug

Add a focused regression test in the relevant test file, or create one such as `tests/test_email_normalization.py`:

```python
from your_module import normalize_email


def test_normalize_email_strips_outer_whitespace_and_lowercases():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

Run only this test, not `pytest` across the whole suite:

```bash
pytest -q tests/test_email_normalization.py -k strips_outer_whitespace_and_lowercases
```

If the test lives in an existing file, use the single test node instead:

```bash
pytest -q path/to/test_file.py::test_normalize_email_strips_outer_whitespace_and_lowercases
```

That should give you a clean red for the normalization bug itself, not the unrelated SMTP failure. The failure we want is the assertion showing whitespace is still being preserved.

Expected red:

```text
E   AssertionError: assert '  alice@example.com  ' == 'alice@example.com'
```

If you run the whole suite and hit `FAILED tests/test_notifications.py::test_sends_signup_email - ConnectionError: SMTP server unavailable`, that is noise for this task, so keep the target narrow until this regression is green.

## Green: smallest fix

Now change only the implementation needed to satisfy that regression:

```python
def normalize_email(email):
    return email.strip().lower()
```

Re-run the same focused test target:

```bash
pytest -q tests/test_email_normalization.py -k strips_outer_whitespace_and_lowercases
```

Expected green:

```text
1 passed
```

## Refactor

No refactor is necessary here. `strip().lower()` is already the minimal clear fix for the reported behavior.

Once that focused regression is green, you can run nearby email-normalization tests if you have them, but I would still avoid the full suite until the SMTP failure is fixed or isolated separately.
