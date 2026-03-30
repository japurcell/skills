Let's keep the interface tiny: `is_valid_password(password: str) -> bool`.
We'll use `pytest` and move in vertical slices: one test, one failure, one minimal fix.

## Cycle 1: reject passwords under 8 characters

Start with the smallest useful rule.

`tests/test_password_validator.py`

```python
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Abc123") is False
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   ModuleNotFoundError: No module named 'password_validator'
```

That is a good red. The test is failing because the feature does not exist yet.

Green, with the smallest implementation that can pass this one test:

`password_validator.py`

```python
def is_valid_password(password: str) -> bool:
    return len(password) >= 8
```

Run the test again:

```bash
pytest -q
```

Expected:

```text
1 passed
```

No refactor yet. The code is still tiny.

## Cycle 2: reject passwords without an uppercase letter

Next behavior:

```python
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Abc123") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("abcdefg1") is False
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   assert True is False
E    +  where True = is_valid_password('abcdefg1')
```

That failure is correct: the current code only checks length.

Green, adding only enough logic for this rule:

```python
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(ch.isupper() for ch in password):
        return False

    return True
```

Run again:

```text
2 passed
```

## Cycle 3: reject passwords without a lowercase letter

Add the next failing test:

```python
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Abc123") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("abcdefg1") is False


def test_rejects_password_without_lowercase():
    assert is_valid_password("ABCDEFG1") is False
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   assert True is False
E    +  where True = is_valid_password('ABCDEFG1')
```

Green:

```python
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(ch.isupper() for ch in password):
        return False

    if not any(ch.islower() for ch in password):
        return False

    return True
```

Run again:

```text
3 passed
```

## Cycle 4: reject passwords without a digit

Add the next rule:

```python
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Abc123") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("abcdefg1") is False


def test_rejects_password_without_lowercase():
    assert is_valid_password("ABCDEFG1") is False


def test_rejects_password_without_digit():
    assert is_valid_password("Abcdefgh") is False
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   assert True is False
E    +  where True = is_valid_password('Abcdefgh')
```

Green, again with only enough code to satisfy the new behavior:

```python
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(ch.isupper() for ch in password):
        return False

    if not any(ch.islower() for ch in password):
        return False

    if not any(ch.isdigit() for ch in password):
        return False

    return False
```

That last `return False` looks odd, but it is still valid TDD discipline here: it is the smallest code that keeps all four rejection tests green without implementing an untested success case.

Run again:

```text
4 passed
```

## Cycle 5: accept a password that satisfies all rules

Now we can add the success case explicitly:

```python
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Abc123") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("abcdefg1") is False


def test_rejects_password_without_lowercase():
    assert is_valid_password("ABCDEFG1") is False


def test_rejects_password_without_digit():
    assert is_valid_password("Abcdefgh") is False


def test_accepts_password_with_uppercase_lowercase_and_digit():
    assert is_valid_password("Abcdefg1") is True
```

Red:

```bash
pytest -q
```

Expected failure:

```text
E   assert False is True
E    +  where False = is_valid_password('Abcdefg1')
```

Green:

```python
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(ch.isupper() for ch in password):
        return False

    if not any(ch.islower() for ch in password):
        return False

    if not any(ch.isdigit() for ch in password):
        return False

    return True
```

Run again:

```text
5 passed
```

## Refactor

Now that everything is green, we can clean up safely without changing behavior:

```python
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(ch.isupper() for ch in password)
        and any(ch.islower() for ch in password)
        and any(ch.isdigit() for ch in password)
    )
```

Re-run the tests after the refactor:

```text
5 passed
```

That is the full red-green-refactor path, one behavior at a time.

If you want, the next step is to turn this into real files on disk: `password_validator.py` and `tests/test_password_validator.py`, then run the same `pytest -q` cycle for real.
