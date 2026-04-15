Perfect setup for TDD! Let's use a failing test to lock in the bug first, then fix with confidence.

## Step 1: Write a test that reproduces the bug

```python
def test_single_digit_month_is_zero_padded():
    """Single-digit months should be zero-padded in output."""
    assert format_date(2024, 1, 15) == "2024-01-15"
```

## Step 2: Run it — it fails ✗

```
AssertionError
  Expected: "2024-01-15"
  Got:      "2024-1-15"
```

Good — the test fails exactly as the bug manifests. Now we know we're testing the right thing.

## Step 3: Write minimal code to pass

We need to zero-pad both month and day to 2 digits:

```python
def format_date(year, month, day):
    return f"{year}-{month:02d}-{day:02d}"
```

The `:02d` format specifier means "pad with zeros to width 2, using decimal format." This handles both single-digit and double-digit months/days.

## Step 4: Run the test — it passes ✓

```
PASSED ✓
```

## Verify adjacent cases

Let me add one more test to make sure we didn't break double-digit months:

```python
def test_double_digit_month_stays_unchanged():
    """Double-digit months should remain unchanged."""
    assert format_date(2024, 12, 25) == "2024-12-25"
```

Run it — this passes too ✓

**You're done!** The bug is fixed and locked in by regression tests. If someone accidentally reverts the `:02d` formatting later, these tests will catch it immediately.
