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

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    cart = carts[cart_id]
    # total_potions = sum([item["quantity"] for _,item in enumerate(cart.get("items",{}))])
    total_potions = 0
    with db.engine.begin() as connection:
        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()
        print(cart["items"])
        for _,item in cart.get("items",{}).items():
            print(item)
            match item["sku"]:
                case "RED_POTION_0":
                    num_red_potions -= item["quantity"]
                case "BLUE_POTION_0":
                    num_blue_potions -= item["quantity"]
                case "GREEN_POTION_0":
                    num_green_potions -= item["quantity"]
            total_potions += item["quantity"]
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions=:num_red_potions,num_green_potions=:num_green_potions,num_blue_potions=:num_blue_potions,gold=:gold"),{"num_red_potions": num_red_potions,"num_blue_potions": num_blue_potions,"num_green_potions":num_green_potions,"gold": gold+int(cart_checkout.payment)})
    return {"total_potions_bought": total_potions, "total_gold_paid": cart_checkout.payment}
