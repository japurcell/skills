The unrelated SMTP failure is noise for this bug fix, so keep the TDD loop focused on the email-normalization tests instead of running the full suite.

Start with the regression test that reproduces the bug:

```python
def test_normalize_email_trims_whitespace_and_lowercases():
    assert normalize_email("  Alice@Example.com  ") == "alice@example.com"
```

Run only the narrowest relevant test target. For example, if this lives in `tests/test_email_utils.py`, run:

```bash
pytest tests/test_email_utils.py -k normalize_email
```

That should fail for the right reason right now: the function lowercases the address, but it does not trim the surrounding whitespace.

Then make the smallest code change that satisfies that test:

```python
def normalize_email(email):
    return email.strip().lower()
```

Re-run the same targeted test command, not the full suite:

```bash
pytest tests/test_email_utils.py -k normalize_email
```

Once that is green, stop. No broader refactor is needed for this bug, and avoiding the full suite keeps the unrelated `test_sends_signup_email` failure from obscuring whether the regression is fixed.
