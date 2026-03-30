# Execution Transcript

## Eval Prompt

My date formatting function has a bug: when the month is a single digit (like January = 1), it outputs '2024-1-15' instead of '2024-01-15'. I want to fix it using TDD — write a failing test that catches this bug first, then fix it. Here's the function:

```python
def format_date(year, month, day):
    return f"{year}-{month}-{day}"
```

## Skill Path

/home/adam/dev/personal/skills/tdd/SKILL.md

## Final Response

We’ll do this as a tight TDD loop around the bug you reported.

Start with the smallest failing test that reproduces the behavior through the public interface. Replace `your_module` with the actual module name:

```python
# test_format_date.py
from your_module import format_date

def test_formats_single_digit_month_with_leading_zero():
    assert format_date(2024, 1, 15) == "2024-01-15"
```

Run the test first:

```bash
pytest -q
```

It should fail for the right reason, something like:

```text
E       AssertionError: assert '2024-1-15' == '2024-01-15'
```

Now make the smallest change that makes that test pass:

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day}"
```

Run the test again. That should put the first slice back to green.

There’s one nearby follow-up case worth locking down, because `YYYY-MM-DD` normally means the day is zero-padded too:

```python
def test_formats_single_digit_day_with_leading_zero():
    assert format_date(2024, 1, 5) == "2024-01-05"
```

That should fail with the current implementation, so make the next minimal fix:

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day:02d}"
```

Re-run the tests. At that point you should be green, and there’s no real refactor to do because the format spec is already the simplest version of the rule.
