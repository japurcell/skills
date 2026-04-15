Let's start by building the interface and the first test. We'll add a method to apply a discount code, then modify `total()` to return the discounted amount.

First, let's set up a test file. I'll assume you're using `pytest`:

```python
# test_shopping_cart.py
import pytest
from shopping_cart import ShoppingCart

def test_save10_applies_10_percent_discount():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    cart.apply_discount_code("SAVE10")
    assert cart.total() == 90.0
```

**Step 1: Run the test — it will fail**

```
FAILED test_shopping_cart.py::test_save10_applies_10_percent_discount
AttributeError: 'ShoppingCart' object has no attribute 'apply_discount_code'
```

That's the expected failure. The feature doesn't exist yet.

**Step 2: Write minimal code to pass this test**

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

**Step 3: Run the test — it passes**

```
PASSED test_shopping_cart.py::test_save10_applies_10_percent_discount
```

✓ Now let's add the next behavior — SAVE20:

```python
def test_save20_applies_20_percent_discount():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    cart.apply_discount_code("SAVE20")
    assert cart.total() == 80.0
```

Run it — this will fail because we only handle SAVE10.

Add the minimal code:

```python
def apply_discount_code(self, code):
    if code == "SAVE10":
        self._discount_percent = 10
    elif code == "SAVE20":
        self._discount_percent = 20
```

Run the test — it passes.

✓ Now let's handle invalid codes:

```python
def test_invalid_discount_code_is_rejected():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    with pytest.raises(ValueError, match="Invalid discount code"):
        cart.apply_discount_code("INVALID")
```

This will fail. Add the minimal handling:

```python
def apply_discount_code(self, code):
    if code == "SAVE10":
        self._discount_percent = 10
    elif code == "SAVE20":
        self._discount_percent = 20
    else:
        raise ValueError(f"Invalid discount code: {code}")
```

Run the test — it passes.

✓ **Refactor opportunity**: Extract the discount mapping.

```python
class ShoppingCart:
    DISCOUNTS = {
        "SAVE10": 10,
        "SAVE20": 20,
    }

    def __init__(self):
        self._items = []
        self._discount_percent = 0

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        if code not in self.DISCOUNTS:
            raise ValueError(f"Invalid discount code: {code}")
        self._discount_percent = self.DISCOUNTS[code]

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        return subtotal * (1 - self._discount_percent / 100)
```

Run all three tests — they all still pass.

At this point you have: the simplest interface that handles valid and invalid codes, and all critical behavior covered by tests. You can add more tests (e.g., "discount only applies after code is set," "multiple items with discount") if there are other edge cases, but these three cover the core feature.
