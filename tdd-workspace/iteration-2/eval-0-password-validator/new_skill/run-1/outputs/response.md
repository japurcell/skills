Let's keep the public API tiny: `is_valid_password(password: str) -> bool`.

We'll do this in strict vertical slices: one test, one red, one minimal green, then move to the next behavior. Since we're simulating this in conversation, I'll show the `pytest -q` command you would run and the kind of failure or pass you should expect.

## Cycle 1: reject passwords under 8 characters

Start with the smallest behavior that matters.

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

That is a good red: the test is failing because the feature does not exist yet.

Green, with the smallest code that can satisfy just this test:

`password_validator.py`

```python
def is_valid_password(password: str) -> bool:
    return len(password) >= 8
```

Run again:

```bash
pytest -q
```

Expected:

```text
1 passed
```

No refactor yet. The implementation is still tiny.

## Cycle 2: reject passwords without an uppercase letter

Before adding more code, make the next missing behavior explicit.

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

That failure is exactly what we want: the current code only checks length.

Green, adding only enough logic for this new rule:

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

Add one more behavior.

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

Next missing rule:

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

Green, still keeping the implementation as small as possible for the tests we actually have:

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

That final `return False` is deliberate. We have only written rejection tests so far, so returning `True` for a valid password would be speculative until we add the acceptance test.

Run again:

```text
4 passed
```

## Cycle 5: accept a password that satisfies all rules

Now we can add the success case through the public interface.

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

Now that we're green, we can safely clean up without changing behavior:

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

That gives you the full red-green-refactor loop, one behavior at a time, without writing tests or implementation ahead of the current slice. If you want, the next step could be adding edge-case tests like symbols being allowed or Unicode letter handling, but the core rule set is covered now.
