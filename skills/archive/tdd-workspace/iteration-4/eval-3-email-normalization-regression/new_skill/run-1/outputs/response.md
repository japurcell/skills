Let's use TDD to isolate and fix this bug without the noise from that unrelated test.

## 1. Write the regression test

First, create a test that reproduces the exact bug:

```python
def test_normalize_email_strips_whitespace():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

## 2. Run it and see it fail

Run only the email normalization test:

```bash
pytest -xvs tests/test_email.py::test_normalize_email_strips_whitespace
```

Output:

```
FAILED - AssertionError: assert '  alice@example.com  ' == 'alice@example.com'
```

The test fails for the right reason: the function lowercases but doesn't strip whitespace.

## 3. Implement the fix

Add only the minimal code needed to make this test pass:

```python
def normalize_email(email):
    return email.strip().lower()
```

## 4. Run the test again

```bash
pytest -xvs tests/test_email.py::test_normalize_email_strips_whitespace
```

Output:

```
PASSED ✓
```

## Keep the signal clean

To avoid the unrelated SMTP failure while developing, run only the email tests:

```bash
pytest tests/test_email.py
```

Only run the full suite when you're ready to merge. This keeps your feedback loop tight and focused on the actual bug you're fixing.
