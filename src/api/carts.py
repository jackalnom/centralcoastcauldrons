from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src.api.database import engine as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

cart_id = 0

carts = {}

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    cart_id +=1
    carts[cart_id] = ({"customer":new_cart.customer})
    return {"cart_id": cart_id-1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return carts[cart_id]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    carts[cart_id]["items"] = carts[cart_id].get("items",[]).push({"item_sku":item_sku,"quantity":cart_item.quantity})
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    cart = carts[cart_id]
    total_potions = sum([item.quantity for item in cart.get("items",[])])
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        num_red_potions, num_red_ml, gold= result.fetchone()
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions=:num_red_potions, gold=:gold"),{"num_red_potions": num_red_potions-total_potions,"gold": gold+cart_checkout.payment})
    return {"total_potions_bought": total_potions, "total_gold_paid": cart_checkout.payment}
