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

Let’s keep this narrow and TDD it through the public function you already have: `format_date(year, month, day)`.
We’ll start with the smallest regression test that proves the bug, make it fail for the right reason, then change only enough code to pass it.

## Cycle 1: month should be zero-padded

Start with the reported bug as a regression test.

`tests/test_format_date.py`

```python
from date_formatter import format_date


def test_zero_pads_single_digit_month():
    assert format_date(2024, 1, 15) == "2024-01-15"
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   AssertionError: assert '2024-1-15' == '2024-01-15'
```

That is the right red: the test reaches the real function and fails on the exact formatting bug you described.

Green, with the smallest code change that fixes this behavior:

`date_formatter.py`

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day}"
```

Run the test again:

```bash
pytest -q
```

Expected:

```text
1 passed
```

## Refactor

I would stop here for this slice. The reported bug is covered by a regression test and the implementation change is minimal.

One thing to note: this fix only pads the month, not the day. That matches the test we wrote and follows TDD discipline by not changing untested behavior. If you want, the next slice would be to add a failing test for single-digit days and then pad `day` the same way.
