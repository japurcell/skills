Perfect! Let's build your password validator using TDD, one behavior at a time.

## Orientation

We'll build a function `is_valid_password(password: str) -> bool` that returns `True` if the password meets all rules, `False` otherwise.

I'll use pytest for testing. If you haven't installed it yet, run:
```bash
pip install pytest
```

Let's tackle the behaviors in this order:
1. Minimum length (8 characters)
2. At least one uppercase letter
3. At least one lowercase letter
4. At least one digit

---

## Step 1: First Test — Minimum Length

Create a file called `test_password.py`:

```python
def test_rejects_password_under_8_chars():
    from password_validator import is_valid_password
    assert is_valid_password("short") is False
```

Create a file called `password_validator.py`:

```python
def is_valid_password(password):
    pass
```

Run the test:
```bash
pytest test_password.py::test_rejects_password_under_8_chars -v
```

**RED:** The test fails because `is_valid_password()` returns `None`, not `False`.

```
FAILED test_password.py::test_rejects_password_under_8_chars - assert None is False
```

Now add the minimal code to pass:

```python
def is_valid_password(password):
    return len(password) >= 8
```

Run the test again:

```bash
pytest test_password.py::test_rejects_password_under_8_chars -v
```

**GREEN:** Test passes.

```
PASSED test_password.py::test_rejects_password_under_8_chars ✓
```

---

## Step 2: Add Uppercase Requirement

Write the next failing test:

```python
def test_requires_at_least_one_uppercase():
    from password_validator import is_valid_password
    assert is_valid_password("lowercase1") is False
```

Run it:

```bash
pytest test_password.py::test_requires_at_least_one_uppercase -v
```

**RED:** The test fails because `"lowercase1"` passes the length check (10 chars) but has no uppercase.

```
FAILED - assert True is False
```

Add minimal code:

```python
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    return True
```

Run the test:

```bash
pytest test_password.py::test_requires_at_least_one_uppercase -v
```

**GREEN:** Test passes.

```
PASSED test_password.py::test_requires_at_least_one_uppercase ✓
```

Run both tests to make sure the first still passes:

```bash
pytest test_password.py -v
```

Both pass ✓

---

## Step 3: Add Lowercase Requirement

New test:

```python
def test_requires_at_least_one_lowercase():
    from password_validator import is_valid_password
    assert is_valid_password("UPPERCASE1") is False
```

Run it:

```bash
pytest test_password.py::test_requires_at_least_one_lowercase -v
```

**RED:** Fails as expected — the password has uppercase and length, but no lowercase.

```
FAILED - assert True is False
```

Add the check:

```python
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    return True
```

Run it:

```bash
pytest test_password.py::test_requires_at_least_one_lowercase -v
```

**GREEN:** Passes ✓

---

## Step 4: Add Digit Requirement

Final test:

```python
def test_requires_at_least_one_digit():
    from password_validator import is_valid_password
    assert is_valid_password("NoDigitsHere") is False
```

Run it:

```bash
pytest test_password.py::test_requires_at_least_one_digit -v
```

**RED:** Fails — has length, uppercase, lowercase, but no digit.

```
FAILED - assert True is False
```

Add the final check:

```python
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True
```

Run it:

```bash
pytest test_password.py::test_requires_at_least_one_digit -v
```

**GREEN:** Passes ✓

---

## Step 5: Verify All Behaviors + Add a Happy Path

Run all tests:

```bash
pytest test_password.py -v
```

All four should pass. Now let's add a test that confirms a valid password actually passes:

```python
def test_accepts_valid_password():
    from password_validator import is_valid_password
    assert is_valid_password("ValidPass123") is True
```

Run it:

```bash
pytest test_password.py::test_accepts_valid_password -v
```

**GREEN:** Already passes! ✓

---

## Step 6: Optional Refactor

The implementation has repetitive `any(c.method() for c in password)` calls. Let's refactor for clarity:

```python
def is_valid_password(password):
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit
```

Run all tests:

```bash
pytest test_password.py -v
```

All pass ✓

You now have a working password validator built test-first, with each rule verified independently!
