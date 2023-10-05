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
    total_num_bottles = 300
    # splits total_num_bottles to even amounts, tries to even out each color
    num_bottles = {color: (total_num_bottles // len(colors)) - getattr(first_row, f"num_{color}_potions") for color in colors}
    current_colors = colors
    # loops until 300 in bottling_list or not enough ml for more
    while total_num_bottles > len(current_colors):
      # loops each color that still has ml
      for color in current_colors.copy():
        # gets possible bottles
        current_ml = getattr(first_row, f"num_{color}_ml")
        current_bottling = 0
        for bottling in bottling_list:
          if bottling["potion_type"] == color_to_potion_ml[color]:
            current_bottling = bottling["quantity"]
        possible_num_bottle = current_ml // 100 - current_bottling
        # if less possible than split, set num_bottles to max possible
        if possible_num_bottle < num_bottles[color]:
          num_bottles[color] = possible_num_bottle
          current_colors.remove(color)
        total_num_bottles -= num_bottles[color]
      # update bottling_list
      for color in num_bottles.keys():
        updated = False
        for bottling in bottling_list:
          if bottling["potion_type"] == color_to_potion_ml[color]:
            bottling["quantity"] += num_bottles[color]
            updated = True
            break
        if updated:
          continue
        if num_bottles[color] != 0:
          bottling_list.append({
                "potion_type": color_to_potion_ml[color],
                "quantity": num_bottles[color],
          })
      # update split of bottles to fill whatever still possibly has ml
      num_bottles = {color: (total_num_bottles // len(colors)) for color in current_colors}
  return bottling_list
