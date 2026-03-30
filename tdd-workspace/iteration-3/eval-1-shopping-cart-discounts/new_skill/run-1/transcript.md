# Execution Transcript

## Eval Prompt

I have a shopping cart module and I want to add a discount code feature using TDD. Discount codes are strings - 'SAVE10' gives 10% off, 'SAVE20' gives 20% off, invalid codes are rejected. Here's the existing code:

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

Add this feature with a strict vertical TDD loop: one behavior at a time through a public method on `ShoppingCart`.

I would introduce `apply_discount_code(code)` and keep `total()` as the public place where discount math is applied.

## Slice 1 (RED -> GREEN): `SAVE10` gives 10% off

Start with one failing test:

```python
from shopping_cart import ShoppingCart


def test_save10_applies_10_percent_discount():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE10")

    assert cart.total() == 135
```

Run only this test first:

```bash
pytest -q -k save10_applies_10_percent_discount
```

Expected RED: `AttributeError` because `apply_discount_code` does not exist yet.

Now add the smallest code to pass only this behavior:

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

Re-run the same test and get GREEN.

## Slice 2 (RED -> GREEN): `SAVE20` gives 20% off

Next missing behavior:

```python
def test_save20_applies_20_percent_discount():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE20")

    assert cart.total() == 120
```

Run:

```bash
pytest -q -k save20_applies_20_percent_discount
```

Expected RED: currently only `SAVE10` is supported.

Minimal change:

```python
def apply_discount_code(self, code):
    if code == 'SAVE10':
        self._discount_percent = 10
    elif code == 'SAVE20':
        self._discount_percent = 20
    else:
        raise ValueError('Invalid discount code')
```

Re-run and get GREEN.

## Slice 3: invalid codes are rejected

Now add:

```python
import pytest


def test_invalid_discount_code_is_rejected():
    cart = ShoppingCart()

    with pytest.raises(ValueError, match='Invalid discount code'):
        cart.apply_discount_code('NOPE')
```

Run just this test:

```bash
pytest -q -k invalid_discount_code_is_rejected
```

If it is already GREEN, keep it as a confirming behavior and move on.

## Refactor (only after all tests are green)

Clean up conditional duplication safely:

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

Then run the focused tests together:

```bash
pytest -q -k "discount_code or save10 or save20"
```

That keeps the loop test-first, behavior-driven, and minimal at each step.
