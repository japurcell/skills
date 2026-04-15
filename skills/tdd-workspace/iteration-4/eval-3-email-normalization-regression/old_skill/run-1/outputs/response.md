Here's how to tackle this with TDD while keeping your signal clean:

## Strategy

Write a focused test file that exercises only the email normalization bug. This way you avoid the unrelated SMTP failure that's polluting your output.

## Step 1: Write the regression test (RED)

Create a new test file, say `tests/test_email_normalization.py`:

```python
def test_normalizes_email_with_whitespace():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

Run just this test:

```bash
pytest tests/test_email_normalization.py -v
```

It fails because the function doesn't strip whitespace:

```
FAILED - AssertionError: assert '  alice@example.com  ' == 'alice@example.com'
```

That's your baseline RED state. The failure message is clear: the whitespace is still there.

## Step 2: Write minimal code (GREEN)

Now implement just what's needed to pass:

```python
def normalize_email(email):
    return email.strip().lower()
```

Run the test again:

```bash
pytest tests/test_email_normalization.py -v
```

It passes:

```
PASSED ✓
```

## Step 3: Build confidence with one more test (optional but recommended)

Add another case to verify the behavior is robust:

```python
def test_normalizes_email_with_whitespace():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"

def test_normalizes_email_without_whitespace():
    assert normalize_email("bob@EXAMPLE.COM") == "bob@example.com"
```

Run both:

```bash
pytest tests/test_email_normalization.py -v
```

Both pass. Now you can confidently integrate this fix back into the main codebase.

## Why this keeps the signal clean

By testing `normalize_email` in isolation, you're not running the full suite with the SMTP failure. Your test output is precise: only this function's behavior matters. Once you're confident it works, you can merge it back to the main code and deal with the SMTP issue separately (which isn't your responsibility right now).
