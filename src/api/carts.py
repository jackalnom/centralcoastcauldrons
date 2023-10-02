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
  return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
  """ """

  return {}


class CartItem(BaseModel):
  quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
  """ """

  return "OK"


class CartCheckout(BaseModel):
  payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
  """ """
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    if first_row.num_red_potions != 0:
      num_bought = first_row.num_red_potions if first_row.num_red_potions <= 20 else 20
      return {"total_potions_bought": num_bought, "total_gold_paid": num_bought * 50}
  return {}
