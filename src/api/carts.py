from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import logging
from src.api import database as db
import sqlalchemy

logger = logging.getLogger("potions")
router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

carts = []


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    logger.info(new_cart)
    newId = len(carts)
    carts.append({})
    """ """
    return {"cart_id": newId}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return carts[cart_id]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    try:
        cart = carts[cart_id]
        cart[item_sku] = cart_item.quantity
        return {"success": True}
    except Exception as error:
        print(error)
        return {"success": False}


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    logger.info("checkout")
    cart = carts[cart_id]
    # only one thing will be in the cart for now
    RED_SKU = "RED_POTION_0"
    red_quantity = cart[RED_SKU]
    POTION_PRICE = 50
    TABLE_NAME = "global_inventory"

    current_inventory = db.get_global_inventory()
    red_potions_count = current_inventory["num_red_potions"]
    gold_count = current_inventory["gold"]

    if red_quantity > red_potions_count:
        print(
            f"ordered {red_quantity} red potions but we only have {red_potions_count} in stock"
        )
        return {"success": False}

    gold_count += POTION_PRICE * red_quantity
    red_potions_count -= red_quantity

    # logic to update database
    update_command = f"UPDATE {TABLE_NAME} SET num_red_potions = {red_potions_count}, gold = {gold_count} WHERE id = 1"
    db.execute(update_command)
    del carts[cart_id]

    return {
        "total_potions_bought": red_quantity,
        "total_gold_paid": POTION_PRICE * red_quantity,
    }
