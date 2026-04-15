# Fix Date Formatting with TDD

Perfect — let's start with a failing test that catches this bug, then fix it.

## Step 1: Write a test that fails

Create a test file to expose the bug:

```python
def test_format_date_pads_single_digit_month():
    assert format_date(2024, 1, 15) == "2024-01-15"

def test_format_date_pads_single_digit_day():
    assert format_date(2024, 5, 9) == "2024-05-09"
```

**Run the test** (it will fail because the current code doesn't pad):

```
FAILED test_format_date_pads_single_digit_month
AssertionError: assert '2024-1-15' == '2024-01-15'
```

Great — we've confirmed the bug. The test is specific about the expected behavior: month and day should always be two digits.

## Step 2: Write minimal code to pass

Fix the function using `zfill()` to pad to 2 digits:

```python
def format_date(year, month, day):
    return f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
```

**Run the tests** — both pass now:

```
PASSED test_format_date_pads_single_digit_month ✓
PASSED test_format_date_pads_single_digit_day ✓
```

## Done

You've fixed the bug via TDD. The tests serve as a specification: any future changes to `format_date` must maintain this zero-padding behavior, or the tests will catch the regression.
