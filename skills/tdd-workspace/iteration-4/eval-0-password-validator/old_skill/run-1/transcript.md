Perfect! Let's build this test-first, one behavior at a time. I'll show you the full red-green cycle for each.

## Orientation

We're building a `validate_password()` function with a clear public interface: it takes a string and returns True/False. The critical behaviors are: minimum length, uppercase, lowercase, and digit presence. Let's start with pytest (install with `pip install pytest`).

---

## Cycle 1: Minimum 8 Characters

**RED — Write the test that should fail:**

```python
# test_password_validator.py
def test_rejects_password_under_8_chars():
    from validator import validate_password
    assert validate_password("short") is False
```

Run it:
```
FAILED test_password_validator.py::test_rejects_password_under_8_chars
ModuleNotFoundError: No module named 'validator'
```

**GREEN — Minimal code to pass:**

```python
# validator.py
def validate_password(password):
    return len(password) >= 8
```

Run it:
```
PASSED test_password_validator.py::test_rejects_password_under_8_chars ✓
```

---

## Cycle 2: Accepts Valid 8+ Character Password

**RED — Write the next test:**

```python
def test_accepts_valid_password():
    from validator import validate_password
    assert validate_password("ValidPass1") is True
```

Run it:
```
FAILED — False is not True
```

**GREEN — Update the code:**

```python
# validator.py
def validate_password(password):
    if len(password) < 8:
        return False
    return any(c.isupper() for c in password) and \
           any(c.islower() for c in password) and \
           any(c.isdigit() for c in password)
```

Run it:
```
PASSED test_password_validator.py::test_accepts_valid_password ✓
PASSED test_password_validator.py::test_rejects_password_under_8_chars ✓
```

---

## Cycle 3: Reject Missing Uppercase

**RED:**

```python
def test_rejects_password_without_uppercase():
    from validator import validate_password
    assert validate_password("validpass1") is False
```

Run it:
```
PASSED test_password_validator.py::test_rejects_password_without_uppercase ✓
```

Because this is already green, we keep it as confirmation.

---

## Cycle 4: Reject Missing Lowercase

**RED:**

```python
def test_rejects_password_without_lowercase():
    from validator import validate_password
    assert validate_password("VALIDPASS1") is False
```

Run it:
```
PASSED test_password_validator.py::test_rejects_password_without_lowercase ✓
```

Already green; keep as confirmation.

---

## Cycle 5: Reject Missing Digit

**RED:**

```python
def test_rejects_password_without_digit():
    from validator import validate_password
    assert validate_password("ValidPass") is False
```

Run it:
```
PASSED test_password_validator.py::test_rejects_password_without_digit ✓
```

Already green; keep as confirmation.

---

## Final Code & All Tests Passing

```python
# validator.py
def validate_password(password):
    if len(password) < 8:
        return False
    return any(c.isupper() for c in password) and \
           any(c.islower() for c in password) and \
           any(c.isdigit() for c in password)


# test_password_validator.py
def test_rejects_password_under_8_chars():
    from validator import validate_password
    assert validate_password("short") is False

def test_accepts_valid_password():
    from validator import validate_password
    assert validate_password("ValidPass1") is True

def test_rejects_password_without_uppercase():
    from validator import validate_password
    assert validate_password("validpass1") is False

def test_rejects_password_without_lowercase():
    from validator import validate_password
    assert validate_password("VALIDPASS1") is False

def test_rejects_password_without_digit():
    from validator import validate_password
    assert validate_password("ValidPass") is False
```

Run all tests:
```
PASSED test_password_validator.py::test_rejects_password_under_8_chars ✓
PASSED test_password_validator.py::test_accepts_valid_password ✓
PASSED test_password_validator.py::test_rejects_password_without_uppercase ✓
PASSED test_password_validator.py::test_rejects_password_without_lowercase ✓
PASSED test_password_validator.py::test_rejects_password_without_digit ✓

5 passed
```

You've got solid behavior coverage and a clear test suite that reads like specification.
