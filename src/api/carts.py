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

    POTION_PRICE = 50
    TABLE_NAME = "global_inventory"
    cart = carts[cart_id]
    inventory = db.get_global_inventory()

    gold_count = inventory["gold"]
    potions_bought = 0
    gold_paid = 0
    for sku, quantity in cart.items():
        color = sku.split("_")[0].lower()

        potion_count = inventory[f"num_f{color}_potions"]

        if quantity > potion_count:
            print(
                f"ordered {quantity} {color} potions but we only have {potion_count} in stock"
            )
            continue

        revenue = POTION_PRICE * quantity
        gold_count += revenue
        potion_count -= quantity

        # logic to update database
        update_command = (
            f"UPDATE {TABLE_NAME} SET num_{color}_potions = {potion_count} WHERE id = 1"
        )
        db.execute(update_command)

        gold_paid += revenue
        potions_bought += quantity

    update_command = f"UPDATE {TABLE_NAME} SET gold = {gold_count} WHERE id = 1"
    del carts[cart_id]

    return {
        "total_potions_bought": potions_bought,
        "total_gold_paid": POTION_PRICE * gold_paid,
    }
