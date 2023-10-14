from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src.api.database import engine as db
from src.api.models import Inventory

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
    global cart_id
    cart_id +=1
    carts[cart_id] = ({"customer":new_cart.customer})
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return carts[cart_id]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    item = {"sku": item_sku, "quantity": cart_item.quantity}
    cart = carts[cart_id]
    if "items" not in cart:
        cart["items"] = {}
    cart["items"][item_sku] = item
    return "OK"


class CartCheckout(BaseModel):
    payment: str

def process_checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    cart = carts[cart_id]
    red_potions_bought = 0
    blue_potions_bought = 0
    green_potions_bought = 0
    gold_paid = int(cart_checkout.payment)
    print(cart)

    for _,item in cart.get("items",{}).items():
        if item["sku"] == "RED_POTION_0":
            red_potions_bought += item["quantity"]
        elif item["sku"] == "BLUE_POTION_0":
            blue_potions_bought += item["quantity"]
        elif item["sku"] == "GREEN_POTION_0":
            green_potions_bought += item["quantity"]
        else:
            raise Exception("Invalid sku")
    return red_potions_bought, blue_potions_bought, green_potions_bought, gold_paid


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    cart = carts[cart_id]
    # total_potions = sum([item["quantity"] for _,item in enumerate(cart.get("items",{}))])
    total_potions = 0
    red_potions_bought, blue_potions_bought, green_potions_bought, gold_paid = process_checkout(cart_id, cart_checkout)
    total_potions += red_potions_bought + blue_potions_bought + green_potions_bought
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    inventory.set_inventory(inventory.gold + gold_paid, inventory.num_red_potions - red_potions_bought, inventory.num_red_ml, inventory.num_blue_potions - blue_potions_bought, inventory.num_blue_ml, inventory.num_green_potions - green_potions_bought, inventory.num_green_ml)
    inventory.sync()
    return {"total_potions_bought": total_potions, "total_gold_paid": cart_checkout.payment}
