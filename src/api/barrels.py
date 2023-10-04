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

colors = ["red", "green", "blue"]
color_to_potion = {
    "red": [1, 0, 0, 0],
    "green": [0, 1, 0, 0],
    "blue": [0, 0, 1, 0],
}
potion_to_color = {tuple(y): x for x, y in color_to_potion.items()}

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
  """ """
  print(barrels_delivered)
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    current_gold = first_row.gold
    for barrel in barrels_delivered:
      color = potion_to_color[tuple(barrel.potion_type)]
      current_gold -= barrel.price * barrel.quantity
      current_ml = getattr(first_row, f"num_{color}_ml")
      current_ml += barrel.ml_per_barrel * barrel.quantity
      connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold={current_gold}, num_{color}_ml={current_ml}"))
  return "OK"

# Gets called once a day
#TODO add priority, multi quantity
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
  """ """
  print(wholesale_catalog)
  buying_barrels = []
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    current_gold = first_row.gold
    split_gold = current_gold / len(colors)
    for color in colors:
      for barrel in wholesale_catalog:
        if barrel.potion_type == color_to_potion[color] and split_gold >= barrel.price:
          buying_barrels.append({
            "sku": barrel.sku,
            "quantity": split_gold // barrel.price,
          })
          break
  return buying_barrels
