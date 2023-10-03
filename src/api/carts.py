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


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("Attempting to generate cart...")
    last_cartid = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM carts"))
        for row in result:
            last_cartid = max(row[0]+1, last_cartid)
        result = connection.execute(sqlalchemy.text(
            f"INSERT INTO carts(cartid, customer_name) VALUES ({last_cartid}, '{new_cart.customer}')"
            ))
    print(f"Cart Generated with ID: {last_cartid}")
    return {"cart_id": last_cartid}

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
        result = connection.execute(sqlalchemy.text(
            f"UPDATE carts SET sku_item0='{item_sku}', quantity_item0={cart_item.quantity}, cost_item0=50 WHERE cartid={cart_id}"
             ))
    print(f"Added {cart_item.quantity} of {item_sku} to cart {cart_item}...")
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    quantity = 0
    unitcost = 0
    # get cart to checkout, assume all red potions
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"SELECT * FROM carts WHERE cartid={cart_id}"))
        for row in result:
            quantity = row[3]
            unitcost = row[4]
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            current_red_pot = row[1]
            current_gold = row[3]
    cost = unitcost*quantity
    # update database
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold={current_gold + cost}, num_red_potions={current_red_pot - quantity}"))
    print(f"Cart ID {cart_id} purchased {quantity} potions and paid {cost} gold")
    return {"total_potions_bought": quantity, "total_gold_paid": cost}
