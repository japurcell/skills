Material uncertainty:

- The prompt says invalid codes are rejected, but does not define the public API for rejection. The response assumes `apply_discount_code(code)` raises `ValueError("Invalid discount code")`.
- The response also assumes discount state is stored on the cart and reflected through `total()` rather than passing a code into `total(code)`.
