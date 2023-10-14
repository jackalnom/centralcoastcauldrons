from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    customer: str

# TODO impliment multicolor and new cart system
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("Attempting to generate cart...")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"INSERT INTO carts(customer_name) \
                                                      VALUES ('{new_cart.customer}') \
                                                      RETURNING cart_id"))
        cart_id = result.first()[0]
    print(f"Cart Generated with ID: {cart_id}")
    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"INSERT INTO carts_transactions(cart_id, sku, quantity) \
                                                      VALUES ({cart_id}, '{item_sku}', {cart_item.quantity})"))
    print(f"Added {cart_item.quantity} of {item_sku} to cart {cart_id}...")

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    total_quantity = 0
    total_cost = 0
    
    # update gold
    with db.engine.begin() as connection:
        result= connection.execute(sqlalchemy.text(
            "UPDATE global_inventory\
            SET gold = global_inventory.gold + carts_transactions.quantity * potion_inventory.cost \
            FROM potion_inventory, carts_transactions \
            WHERE potion_inventory.sku = carts_transactions.sku and carts_transactions.cart_id = :cart_id\
            RETURNING carts_transactions.quantity * potion_inventory.cost"),
            [{"cart_id":cart_id}]
            )
    total_cost = result.first()[0]
    
    with db.engine.begin() as connection:
        result= connection.execute(sqlalchemy.text(
            "UPDATE potion_inventory \
             SET quantity = potion_inventory.quantity - carts_transactions.quantity \
             FROM carts_transactions \
             WHERE potion_inventory.sku = carts_transactions.sku and carts_transactions.cart_id = :cart_id \
             RETURNING carts_transactions.quantity"),
             [{"cart_id":cart_id}]
             )
    for row in result:
        total_quantity += row[0]

    print(f"Cart ID {cart_id} purchased {total_quantity} potions and paid {total_cost} gold")

    return {"total_potions_bought": total_quantity, "total_gold_paid": total_cost}
