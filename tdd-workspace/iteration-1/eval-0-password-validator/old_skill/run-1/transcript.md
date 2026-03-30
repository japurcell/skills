# Execution Transcript

## Eval Prompt

I need to write a password validator in Python using TDD. The rules are: at least 8 characters, must have at least one uppercase letter, one lowercase letter, and one digit. Let's build it test-first — start with the first test, show me the red-green cycle, then keep going one behavior at a time.

## Skill Path

/home/adam/dev/personal/skills/tdd-workspace/skill-snapshot/SKILL.md

## Final Response

We’ll keep this strictly TDD and use `pytest` with a small public interface:

- `is_valid_password(password: str) -> bool`

I’ll show each red-green cycle explicitly and only add code for the behavior under test.

## Cycle 1: minimum length

### Red

Start with the first useful behavior: reject passwords shorter than 8 characters.

```python
# test_password_validator.py
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Short1") is False
```

If we run `pytest`, this should fail first because `password_validator.py` and `is_valid_password` do not exist yet.

Expected red:

```text
E   ModuleNotFoundError: No module named 'password_validator'
```

### Green

Write the smallest implementation that makes that test pass.

```python
# password_validator.py
def is_valid_password(password: str) -> bool:
    return len(password) >= 8
```

Run `pytest` again.

Expected green:

```text
1 passed
```

## Cycle 2: uppercase requirement

### Red

Next behavior: reject a password that has length and a digit, but no uppercase letter.

```python
from password_validator import is_valid_password


def test_rejects_password_without_uppercase():
    assert is_valid_password("lowercase1") is False
```

This should fail because the current implementation only checks length.

Expected red:

```text
E   AssertionError: assert True is False
```

### Green

Add only the uppercase rule.

```python
# password_validator.py
def is_valid_password(password: str) -> bool:
    return len(password) >= 8 and any(char.isupper() for char in password)
```

Run the tests again.

Expected green:

```text
2 passed
```

## Cycle 3: lowercase requirement

### Red

Now reject a password with length, uppercase, and digit, but no lowercase letter.

```python
from password_validator import is_valid_password


def test_rejects_password_without_lowercase():
    assert is_valid_password("UPPERCASE1") is False
```

That should fail because uppercase-only strings currently pass.

Expected red:

```text
E   AssertionError: assert True is False
```

### Green

Add only the lowercase rule.

```python
# password_validator.py
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
    )
```

Run the tests again.

Expected green:

```text
3 passed
```

## Cycle 4: digit requirement

### Red

Next behavior: reject a password with length, uppercase, and lowercase, but no digit.

```python
from password_validator import is_valid_password


def test_rejects_password_without_digit():
    assert is_valid_password("Password") is False
```

This should fail because we still are not checking for digits.

Expected red:

```text
E   AssertionError: assert True is False
```

### Green

Add only the digit rule.

```python
# password_validator.py
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
    )
```

Run the tests again.

Expected green:

```text
4 passed
```

## Cycle 5: valid password acceptance

### Red

We have covered rejection cases for each rule. Now add the positive behavior: accept a password that satisfies all requirements.

```python
from password_validator import is_valid_password


def test_accepts_password_with_min_length_uppercase_lowercase_and_digit():
    assert is_valid_password("Password1") is True
```

This should already pass with the current implementation. If it does, that is fine: it confirms the behavior we built up through the previous cycles.

Expected result:

```text
5 passed
```

## Final code

```python
# test_password_validator.py
from password_validator import is_valid_password


def test_rejects_password_under_8_chars():
    assert is_valid_password("Short1") is False


def test_rejects_password_without_uppercase():
    assert is_valid_password("lowercase1") is False


def test_rejects_password_without_lowercase():
    assert is_valid_password("UPPERCASE1") is False


def test_rejects_password_without_digit():
    assert is_valid_password("Password") is False


def test_accepts_password_with_min_length_uppercase_lowercase_and_digit():
    assert is_valid_password("Password1") is True
```

```python
# password_validator.py
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
    )
```

## Refactor

There is no strong refactor needed yet. The implementation is still small and the tests describe behavior through the public function rather than internal details, which is exactly what we want in TDD.

If you want, the next step is for me to show this as an actual file-by-file session exactly as you would type and run it with `pytest`.
