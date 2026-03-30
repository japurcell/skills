# Execution Transcript

## Eval Prompt

My date formatting function has a bug: when the month is a single digit (like January = 1), it outputs '2024-1-15' instead of '2024-01-15'. I want to fix it using TDD — write a failing test that catches this bug first, then fix it. Here's the function:

```python
def format_date(year, month, day):
    return f"{year}-{month}-{day}"
```

## Skill Path

/home/adam/dev/personal/skills/tdd-workspace/skill-snapshot/SKILL.md

## Final Response

Use one tight red-green cycle here.

First, write a failing regression test that describes the behavior you want:

```python
# test_format_date.py
from your_module import format_date


def test_formats_single_digit_month_with_zero_padding():
    assert format_date(2024, 1, 15) == "2024-01-15"
```

Now run the test. It should fail for the right reason, because the current function returns `2024-1-15`:

```text
E       AssertionError: assert '2024-1-15' == '2024-01-15'
```

Then make the smallest change that makes that test pass:

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day}"
```

Run the test again. Once it passes, you are back to green.

If you want to continue the TDD loop after this, the next useful test would be a single-digit day so the function consistently produces `YYYY-MM-DD`.
