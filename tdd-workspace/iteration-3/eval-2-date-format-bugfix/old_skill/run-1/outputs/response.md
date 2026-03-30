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
