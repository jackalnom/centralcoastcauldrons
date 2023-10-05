from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from ..colors import colors, color_to_potion_ml, potion_ml_to_color

router = APIRouter(
  prefix="/bottler",
  tags=["bottler"],
  dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
  potion_type: list[int]
  quantity: int


@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
  """ """
  print(potions_delivered)
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    for potion in potions_delivered:
      color = potion_ml_to_color[tuple(potion.potion_type)]
      current_potions = getattr(first_row, f"num_{color}_potions") + potion.quantity
      current_ml = getattr(first_row, f"num_{color}_ml") - 100 * potion.quantity
      connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_potions={current_potions}, num_{color}_ml={current_ml}"))
  return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
  """
  Go from barrel to bottle.
  """
  # Each bottle has a quantity of what proportion of red, blue, and
  # green potion to add.
  # Expressed in integers from 1 to 100 that must sum up to 100.

  # Initial logic: bottle all barrels into red potions.
  bottling_list = []
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    for color in colors:
      current_ml = getattr(first_row, f"num_{color}_ml")
      if current_ml >= 100:
        bottling_list.append({
          "potion_type": color_to_potion_ml[color],
          "quantity": current_ml // 100,
        })
  return bottling_list
