from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
  prefix="/barrels",
  tags=["barrels"],
  dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
  sku: str

  ml_per_barrel: int
  potion_type: list[int]
  price: int

  quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
  """ """
  print(barrels_delivered)
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    current_gold = first_row.gold
    current_num_red_ml = first_row.num_red_ml
    for barrel in barrels_delivered:
      current_gold -= barrel.price * barrel.quantity
      current_num_red_ml += barrel.ml_per_barrel * barrel.quantity
      connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold={current_gold}, num_red_ml={current_num_red_ml}"))
  
  return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
  """ """
  print(wholesale_catalog)
  buying_barrels = []
  color_to_potion = {
    "red": [1, 0, 0, 0],
    "green": [0, 1, 0, 0],
    "blue": [0, 0, 1, 0],
  }
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    current_gold = first_row.gold
    for color in ["red", "green", "blue"]:
      if getattr(first_row, f"num_{color}_potions") < 10:
        for barrel in wholesale_catalog:
          if barrel.potion_type == color_to_potion[color] and current_gold >= barrel.price:
            buying_barrels.append({
              "sku": barrel.sku,
              "quantity": 1,
            })
            current_gold -= barrel.price
            break
  return buying_barrels
