# Execution Transcript

## Eval Prompt

I have a shopping cart module and I want to add a discount code feature using TDD. Discount codes are strings — 'SAVE10' gives 10% off, 'SAVE20' gives 20% off, invalid codes are rejected. Here's the existing code:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def total(self):
        return sum(item['price'] for item in self._items)
```

Help me add the discount code feature test-first.

## Skill Path

/home/adam/dev/personal/skills/tdd/SKILL.md

## Final Response

I’d drive this through one public API decision first: add `apply_discount_code(code)` to `ShoppingCart`. A valid code sets a cart-level discount, `total()` returns the discounted total, and an invalid code raises `ValueError`.

Let’s do it in small red-green-refactor slices with `pytest`.

## Slice 1: `SAVE10` works

Start with the smallest useful behavior:

```python
import pytest
from shopping_cart import ShoppingCart


def test_applies_save10_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Laptop sleeve", 100)

    cart.apply_discount_code("SAVE10")

    assert cart.total() == 90
```

Run just this test:

```bash
pytest -q -k save10
```

This should fail for the right reason: `ShoppingCart` does not have `apply_discount_code` yet.

Now add only enough code to make that pass:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        if code == 'SAVE10':
            self._discount_percent = 10
        else:
            raise ValueError('Invalid discount code')

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Re-run:

```bash
pytest -q -k save10
```

That should now go green.

## Slice 2: `SAVE20` works

Next behavior:

```python
def test_applies_save20_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Keyboard", 100)

    cart.apply_discount_code("SAVE20")

    assert cart.total() == 80
```

Run it:

```bash
pytest -q -k save20
```

This should fail because the code currently only accepts `SAVE10`.

Make the smallest change that passes both tests:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        if code == 'SAVE10':
            self._discount_percent = 10
        elif code == 'SAVE20':
            self._discount_percent = 20
        else:
            raise ValueError('Invalid discount code')

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Re-run the focused discount tests.

## Slice 3: invalid codes are rejected

Now lock in the rejection behavior:

```python
import pytest


def test_rejects_invalid_discount_code():
    cart = ShoppingCart()

    with pytest.raises(ValueError, match='Invalid discount code'):
        cart.apply_discount_code('NOTREAL')
```

Run it:

```bash
pytest -q -k discount
```

This may already pass. If it does, that is fine; the test is still valuable because it proves the behavior explicitly.

## Refactor once green

Now that all three behaviors are covered, remove the duplication in `apply_discount_code`:

```python
class ShoppingCart:
    DISCOUNT_CODES = {
        'SAVE10': 10,
        'SAVE20': 20,
    }

    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        try:
            self._discount_percent = self.DISCOUNT_CODES[code]
        except KeyError:
            raise ValueError('Invalid discount code')

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Re-run the relevant tests after the refactor:

```bash
pytest -q
```

At this point you have a clean TDD sequence:

1. Write one failing test for `SAVE10`.
2. Add minimal code to pass it.
3. Write one failing test for `SAVE20`.
4. Add minimal code to pass it.
5. Write the invalid-code test.
6. Refactor the branching into a lookup table.

If you want, I can continue with the next TDD step and show what the final `pytest` test file would look like assembled in one place.
