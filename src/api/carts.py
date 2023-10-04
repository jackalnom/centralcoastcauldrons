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


cart_id = 0
carts = {}

@router.post("/")
def create_cart(new_cart: NewCart):
  """ """
  global cart_id
  cart_id += 1
  carts[cart_id] = {"customer": new_cart.customer, "sku": "", "quantity": 0}
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
  carts[cart_id]["sku"] = item_sku
  carts[cart_id]["quantity"] = cart_item.quantity
  return "OK"


class CartCheckout(BaseModel):
  payment: str

#TODO fix concurrency, add different prices
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
  """ """
  print(cart_checkout.payment) # check to see cartcheckout
  print(carts) # check to see all carts
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory FOR UPDATE"))
    first_row = result.first()
    current_gold = first_row.gold
    sku = carts[cart_id]["sku"]
    color = sku.split('_')[0].lower()
    current_potions = getattr(first_row, f"num_{color}_potions")
    if current_potions != 0:
      num_bought = carts[cart_id]["quantity"] if carts[cart_id]["quantity"] <= current_potions else current_potions
      gold_received = num_bought * 50
      current_potions -= num_bought
      current_gold += gold_received
      connection.execute(sqlalchemy.text(f"UPDATE global_inventory \
                                         SET num_{color}_potions={current_potions}, \
                                         gold={current_gold}"))
      connection.commit()
      print({"total_potions_bought": num_bought, "total_gold_paid": gold_received})
      return {"total_potions_bought": num_bought, "total_gold_paid": gold_received}
  return {}
