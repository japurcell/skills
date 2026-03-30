Start with the public interface before the first test. Given the existing class, a small, testable design is to add `apply_discount_code(code)` and keep `total()` as the place where the discounted amount is returned. For invalid codes, I’d reject them by raising `ValueError`.

Since this is Python and there’s no test scaffold shown, I’d use `pytest`.

```python
import pytest
from shopping_cart import ShoppingCart


def test_save10_applies_10_percent_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE10")

    assert cart.total() == 135
```

Run that first. It should fail because `ShoppingCart` does not yet have `apply_discount_code`.

Then write the smallest implementation that makes only that test pass:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        if code == "SAVE10":
            self._discount_percent = 10

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Run the test again. It should pass.

Next, add the rejection behavior as a separate red-green cycle:

```python
def test_invalid_discount_code_is_rejected():
    cart = ShoppingCart()

    with pytest.raises(ValueError, match="Invalid discount code"):
        cart.apply_discount_code("BADCODE")
```

Run it. It should fail because invalid codes are currently ignored.

Make the minimal change:

```python
def apply_discount_code(self, code):
    if code == "SAVE10":
        self._discount_percent = 10
    else:
        raise ValueError("Invalid discount code")
```

Run both tests. They should pass.

Now add the next supported behavior:

```python
def test_save20_applies_20_percent_discount_to_total():
    cart = ShoppingCart()
    cart.add_item("Book", 100)
    cart.add_item("Pen", 50)

    cart.apply_discount_code("SAVE20")

    assert cart.total() == 120
```

That should fail because only `SAVE10` is implemented. Make the smallest change to get back to green:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        if code == "SAVE10":
            self._discount_percent = 10
        elif code == "SAVE20":
            self._discount_percent = 20
        else:
            raise ValueError("Invalid discount code")

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Once all three tests are green, do a small refactor to remove the branching duplication while keeping behavior the same:

```python
class ShoppingCart:
    DISCOUNT_CODES = {
        "SAVE10": 10,
        "SAVE20": 20,
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
            raise ValueError("Invalid discount code")

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

That gives you a clean TDD sequence:

1. Write one failing test for `SAVE10`.
2. Make it pass with the smallest implementation.
3. Add one failing test for invalid codes.
4. Make it pass.
5. Add one failing test for `SAVE20`.
6. Make it pass.
7. Refactor only after everything is green.

If you want, I can turn this into a single `pytest` test file plus the final production class in one block.
