I’d drive this through one small public API change: add `apply_discount_code(code)` to `ShoppingCart`. The cart keeps owning price calculation, so `total()` should return the discounted total, and invalid codes should be rejected with `ValueError`.

Use `pytest`, and keep the loop vertical: one failing test, one minimal change, repeat.

## Slice 1: `SAVE10` applies a discount

Start with the smallest useful behavior:

```python
from shopping_cart import ShoppingCart


def test_save10_applies_10_percent_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE10")

    assert cart.total() == 135
```

Run the narrow test:

```bash
pytest -q -k save10
```

This should fail for the right reason: `ShoppingCart` has no `apply_discount_code` yet.

Add only enough production code to make that pass:

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

Re-run `pytest -q -k save10` and get back to green before moving on.

## Slice 2: invalid codes are rejected

Now add the next missing behavior:

```python
import pytest


def test_invalid_discount_code_is_rejected():
    cart = ShoppingCart()

    with pytest.raises(ValueError, match='Invalid discount code'):
        cart.apply_discount_code('BADCODE')
```

Run it:

```bash
pytest -q -k invalid_discount_code
```

This should already be a real red/green check against the current implementation. If it passes, keep it and move on. If it fails, make only the smallest change needed to raise `ValueError` for unknown codes.

At this point, the current `apply_discount_code` implementation is still minimal and acceptable.

## Slice 3: `SAVE20` applies a discount

Now add the second valid code:

```python
def test_save20_applies_20_percent_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE20")

    assert cart.total() == 120
```

Run it:

```bash
pytest -q -k save20
```

This should fail because only `SAVE10` is supported.

Make the smallest change to pass all current tests:

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

Re-run the focused discount tests and make sure they are all green.

## Refactor once green

Now that the behavior is covered, remove the branching duplication without changing the interface:

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

Then run the relevant tests again:

```bash
pytest -q
```

That keeps the TDD loop honest:

1. Write one failing test for `SAVE10`.
2. Make it pass with the smallest implementation.
3. Add one test for invalid codes.
4. Confirm rejection behavior.
5. Add one failing test for `SAVE20`.
6. Make it pass.
7. Refactor only after everything is green.

If you want, the next step would be assembling those three tests into a single `test_shopping_cart.py` file and then applying each production change one slice at a time.
