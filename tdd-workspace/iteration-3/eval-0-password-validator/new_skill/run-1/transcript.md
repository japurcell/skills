# Execution Transcript

- Read and followed the TDD skill at `/home/adam/dev/personal/skills/tdd/SKILL.md`.
- Simulated the assistant conversation response only.
- Did not modify repository source files or implement workspace code.

## Eval Prompt

I need to write a password validator in Python using TDD. The rules are: at least 8 characters, must have at least one uppercase letter, one lowercase letter, and one digit. Let's build it test-first — start with the first test, show me the red-green cycle, then keep going one behavior at a time.

## Skill Path

/home/adam/dev/personal/skills/tdd/SKILL.md

## Final Response

Let's do this in strict TDD vertical slices with a tiny public API:

`is_valid_password(password: str) -> bool`

I’ll show each **Red -> Green -> (optional) Refactor** cycle one behavior at a time.

## Cycle 1: minimum length (at least 8)

Start with the smallest useful failing test.

`tests/test_password_validator.py`

```python
from password_validator import is_valid_password


def test_rejects_password_shorter_than_8_chars():
    assert is_valid_password("Abc123") is False
```

Run (Red):

```bash
pytest -q
```

Expected failure:

```text
E   ModuleNotFoundError: No module named 'password_validator'
```

Great red: feature does not exist yet.

Now minimal Green implementation.

`password_validator.py`

```python
def is_valid_password(password: str) -> bool:
    return len(password) >= 8
```

Run again:

```text
1 passed
```

## Cycle 2: must contain uppercase

Add only the next missing behavior.

```python
from password_validator import is_valid_password


def test_rejects_password_shorter_than_8_chars():
    assert is_valid_password("Abc123") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("abcdefg1") is False
```

Run (Red):

```text
E   assert True is False
E    +  where True = is_valid_password('abcdefg1')
```

Minimal Green:

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

## Cycle 3: must contain lowercase

```python
def test_rejects_password_without_lowercase():
    assert is_valid_password("ABCDEFG1") is False
```

Run (Red):

```text
E   assert True is False
E    +  where True = is_valid_password('ABCDEFG1')
```

Minimal Green:

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

## Cycle 4: must contain digit

```python
def test_rejects_password_without_digit():
    assert is_valid_password("Abcdefgh") is False
```

Run (Red):

```text
E   assert True is False
E    +  where True = is_valid_password('Abcdefgh')
```

Minimal Green (still strict to current tests):

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

That `return False` is intentional for now because we have only written rejection tests so far.

Run again:

```text
4 passed
```

## Cycle 5: valid password should pass

Now add the positive behavior.

```python
def test_accepts_password_with_uppercase_lowercase_and_digit():
    assert is_valid_password("Abcdefg1") is True
```

Run (Red):

```text
E   assert False is True
E    +  where False = is_valid_password('Abcdefg1')
```

Minimal Green:

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

## Refactor (only after green)

Now simplify while preserving behavior:

```python
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(ch.isupper() for ch in password)
        and any(ch.islower() for ch in password)
        and any(ch.isdigit() for ch in password)
    )
```

Re-run tests:

```text
5 passed
```

That is the full red-green-refactor flow, one behavior at a time, test-first throughout.
