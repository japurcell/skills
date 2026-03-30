Let’s do this with a strict TDD loop: reproduce the bug with one failing regression test, make the smallest fix, then stop.

## 1. RED: Write the failing regression test first

Create a test like this:

```python
from date_formatter import format_date


def test_zero_pads_single_digit_month():
    assert format_date(2024, 1, 15) == "2024-01-15"
```

Run it:

```bash
pytest -q
```

Expected failure (the important part):

```text
AssertionError: assert '2024-1-15' == '2024-01-15'
```

This is a good RED because it fails for the exact bug you reported.

## 2. GREEN: Make the smallest code change to pass

Update the function to zero-pad the month:

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day}"
```

Run the test again:

```bash
pytest -q
```

Now it should pass.

## 3. REFACTOR: Keep it minimal

No refactor is needed yet. The regression is covered and fixed with the smallest change.

If you want, the next TDD slice is adding a failing test for single-digit days and then padding `day` too.
