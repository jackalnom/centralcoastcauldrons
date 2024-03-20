# API Specification

## 1. Customer Purchasing

The API calls are made in this sequence when making a purchase:
1. `Get Catalog`
2. `New Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`

### 1.1. Get Catalog - `/catalog/` (GET)

Retrieves the catalog of items. Each unique item combination should have only a single price. You can have at most 6 potion SKUs offered in your catalog at one time.

**Returns**:

```json
[
    {
        "sku": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "name": "string",
        "quantity": "integer", /* Between 1 and 10000 */
        "price": "integer", /* Between 1 and 500 */
        "potion_type": [r, g, b, d] /* r, g, b, d are integers that add up to exactly 100 */
    }
]
```

### 1.2. New Cart - `/carts/` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
  "customer": "string"
}
```

**Returns**:

```json
{
    "cart_id": "string" /* This id will be used for future calls to add items and checkout */
}
``` 

### 1.3. Add Item to Cart - `/carts/{cart_id}/items/{item_sku}` (PUT)

Updates the quantity of a specific item in a cart. 

**Request**:

```json
{
  "quantity": "integer"
}
```

**Returns**:

```json
{
    "success": "boolean"
}
```

### 1.4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Handles the checkout process for a specific cart.

**Request**:

```json
{
  "payment": "string",
}
```

**Returns**:

```json
{
    "total_potions_bought": "integer"
    "total_gold_paid": "integer"
}
```

## 2. Bottling

The API calls are made in this sequence when the bottler comes:
1. `Get Bottle Plan`
2. `Deliver Bottles`

### 2.1. Get Bottle Plan - `/bottler/plan` (POST)

Gets the plan for bottling potions.

**Returns**:

```json
[
    {
        "potion_type": [r, g, b, d],
        "quantity": "integer"
    }
]
```

### 2.2. Deliver Bottles - `/bottler/deliver` (POST)

Posts delivery of potions.

**Request**:

```json
[
  {
    "potion_type": [r, g, b, d],
    "quantity": "integer"
  }
]
```

## 3. Barrel Purchases

The API calls are made in this sequence when Barrel Purchases can be made:
1. `Get Barrel Purchase Plan`
2. `Deliver Barrels`

### 3.1. Get Barrel Purchase Plan - `/barrels/plan` (POST)

Gets the plan for purchasing wholesale barrels.

**Request**:

```json
[
  {
    "sku": "string",
    "ml_per_barrel": "integer",
    "potion_type": "integer",
    "price": "integer",
    "quantity": "integer"
  }
]
```

**Returns**:

```json
[
    {
        "sku": "string", /* Must match a sku from the catalog just passed in this call */
        "quantity": "integer" /* A number between 1 and the quantity available for sale */
    }
]
```

### 3.2. Deliver Barrels - `/barrels/deliver` (POST)

Posts delivery of barrels.

**Request**:

```json
[
  {
    "sku": "string",
    "ml_per_barrel": "integer",
    "potion_type": "integer",
    "price": "integer",
    "quantity": "integer"
  }
]
```

### 4. Admin Functions

### 4.1. Reset Shop - `/admin/reset` (POST)

A call to reset shop will delete all inventory and in-flight carts and reset gold back to 100.

### 4.2. Shop Info - `/admin/shop_info` (GET)

Returns the name of the shop and who the shop owner is.

```json
{
    "shop_name": "string",
    "shop_owner": "string",
}
```
