# Test-Driving Discount Codes

Great! Let's use TDD to add this. We'll build it step-by-step with vertical slices: one test → minimal code → next test.

## Step 1: Set Up Testing

First, make sure you have pytest:

```bash
pip install pytest
```

Create a `test_shopping_cart.py` file:

```python
from shopping_cart import ShoppingCart

def test_apply_save10_discount():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    cart.apply_discount_code("SAVE10")
    assert cart.total() == 90  # 100 * 0.9
```

**Run it:**
```
pytest test_shopping_cart.py
```

It will fail: `AttributeError: 'ShoppingCart' object has no attribute 'apply_discount_code'`

That's expected—we haven't implemented it yet.

## Step 2: Minimal Implementation

Add just enough to make the test pass:

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._discount_code = None

    def add_item(self, name, price):
        self._items.append({'name': name, 'price': price})

    def apply_discount_code(self, code):
        self._discount_code = code

    def total(self):
        subtotal = sum(item['price'] for item in self._items)
        if self._discount_code == "SAVE10":
            return subtotal * 0.9
        elif self._discount_code == "SAVE20":
            return subtotal * 0.8
        return subtotal
```

**Run it again:**
```
pytest test_shopping_cart.py
```

✅ Now it passes.

## Step 3: Next Behavior — SAVE20

```python
def test_apply_save20_discount():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    cart.apply_discount_code("SAVE20")
    assert cart.total() == 80  # 100 * 0.8
```

Run it—it passes because we already handled it in the minimal code.

## Step 4: Invalid Codes Should Be Rejected

```python
def test_rejects_invalid_discount_code():
    cart = ShoppingCart()
    cart.add_item("Widget", 100)
    with pytest.raises(ValueError):
        cart.apply_discount_code("INVALID")
    assert cart.total() == 100  # full price, no discount applied
```

Run it—it fails. Now add validation:

```python
def apply_discount_code(self, code):
    if code not in ["SAVE10", "SAVE20"]:
        raise ValueError(f"Invalid discount code: {code}")
    self._discount_code = code
```

✅ Now all three tests pass.

## Next Steps

From here, consider tests for:
- Multiple items with discount
- Zero/empty cart with discount code
- Changing discount codes mid-session

What would be most useful to test next?
