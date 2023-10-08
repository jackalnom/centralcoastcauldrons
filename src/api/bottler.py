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

colors = ["red", "green", "blue", "dark"]

class PotionInventory(BaseModel):
  potion_type: list[int]
  quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
  """ """
  print(potions_delivered)
  with db.engine.begin() as connection:
    for potion in potions_delivered:
      # update number of potions in potion_inventory
      connection.execute(sqlalchemy.text("""
          UPDATE potion_inventory
          SET num_potion = num_potion + :add_potions
          WHERE potion_type = :potion_type
          """), {"add_potions": potion.quantity, "potion_type": potion.potion_type})
      # update number of ml in global_inventory
      for i in range(len(colors)):
        connection.execute(sqlalchemy.text(f"""
          UPDATE global_inventory
          SET num_{colors[i]}_ml = num_{colors[i]}_ml - :add_ml
          """), {"add_ml": potion.potion_type[i] * potion.quantity})
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
    global_inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
    number_of_potions = connection.execute(sqlalchemy.text("""
        SELECT
          SUM(num_potion) AS number_of_potions
        FROM potion_inventory
        """)).first().number_of_potions
    potion_inventory = connection.execute(sqlalchemy.text("""
        SELECT
          potion_type,
          num_potion
        FROM potion_inventory
        """)).fetchall()
    # 300 max total bottles
    total_num_bottles = 300 - number_of_potions
    current_ml = [global_inventory.num_red_ml, global_inventory.num_green_ml, global_inventory.num_blue_ml, global_inventory.num_dark_ml]
    # splits total_num_bottles to even amounts, tries to even out each color
    current_types = []
    num_bottles = {}
    for row in potion_inventory:
      num_each = total_num_bottles // len(potion_inventory) - row[1]
      if num_each > 0:
        current_types.append(row[0])
        num_bottles[tuple(row[0])] = num_each
    # loops until 300 in bottling_list or not enough ml for more
    while total_num_bottles > len(current_types) and len(current_types) != 0:
      # loops each type that can still be bottled
      for type in current_types.copy():
        # gets possible bottles
        possible_num_bottle = min(
            current_ml[0] // type[0] if type[0] != 0 else 300,
            current_ml[1] // type[1] if type[1] != 0 else 300,
            current_ml[2] // type[2] if type[2] != 0 else 300,
            current_ml[3] // type[3] if type[3] != 0 else 300
        )
        # if less possible than split, set num_bottles to max possible
        if possible_num_bottle < num_bottles[tuple(type)]:
          num_bottles[tuple(type)] = possible_num_bottle
          current_types.remove(type)
        total_num_bottles -= num_bottles[tuple(type)]
        # updates ml available
        for i in range(len(current_ml)):
          current_ml[i] -= type[i] * num_bottles[tuple(type)]
      # update bottling_list
      for type in num_bottles.keys():
          updated = False
          for bottling in bottling_list:
            if bottling["potion_type"] == type:
              bottling["quantity"] += num_bottles[tuple(type)]
              updated = True
              break
          if updated:
            continue
          if num_bottles[tuple(type)] != 0:
            bottling_list.append({
                  "potion_type": type,
                  "quantity": num_bottles[tuple(type)],
            })
      # update split of bottles to fill whatever still possibly has ml
      num_bottles = {tuple(type): (total_num_bottles // len(current_types)) for type in current_types}
  return bottling_list
