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
                                                      VALUES ('{new_cart.customer}')"))
        result = connection.execute(sqlalchemy.text(f"SELECT cart_id \
                                                      FROM carts \
                                                      WHERE customer_name = '{new_cart.customer}'"))
    for row in result:
        cart_id = row[0]
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
    print(f"Added {cart_item.quantity} of {item_sku} to cart {cart_item}...")
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    quantity = 0
    cost = 0
    sku_list = []
    with db.engine.begin() as connection:
        result_ts = connection.execute(sqlalchemy.text(f"SELECT * FROM carts_transactions WHERE cart_id={cart_id}"))
        result_gold = connection.execute(sqlalchemy.text(f"SELECT gold FROM global_inventory"))
    for row in result_ts:
        sku_list += [row[2]]
        with db.engine.begin() as connection:
            result_potion_inv = connection.execute(sqlalchemy.text(f"SELECT quantity,cost FROM potion_inventory WHERE sku={sku}"))
        
    

    print(f"Cart ID {cart_id} purchased {quantity} potions and paid {cost} gold")
    return {"total_potions_bought": quantity, "total_gold_paid": cost}
