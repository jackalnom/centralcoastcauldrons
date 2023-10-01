from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
    current_num_red_potions = first_row.num_red_potions
    current_num_red_ml = first_row.num_red_ml
    for potion in potions_delivered:
      if potion.potion_type == [100, 0, 0, 0]:
        current_num_red_potions += potion.quantity
        current_num_red_ml -= 100 * potion.quantity
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions={current_num_red_potions}, num_red_ml={current_num_red_ml}"))
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
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    if first_row.num_red_ml >= 100:
      return [
        {
          "potion_type": [100, 0, 0, 0],
          "quantity": first_row.num_red_ml/100,
        }
      ]
  return []
