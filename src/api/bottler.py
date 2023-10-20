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
MAX_NUM_EACH = 30

class PotionInventory(BaseModel):
  potion_type: list[int]
  quantity: int


@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
  """ """
  print(potions_delivered)
  with db.engine.begin() as connection:
    # for logging
    used_ml = [0, 0, 0, 0]
    for potion in potions_delivered:
      # update number of potions in potion_inventory
      connection.execute(sqlalchemy.text("""
          UPDATE potion_inventory
          SET num_potion = num_potion + :add_potions
          WHERE potion_type = :potion_type
          """), {"add_potions": potion.quantity, "potion_type": potion.potion_type})
      # update number of ml in global_inventory
      for i in range(len(colors)):
        potion_ml = potion.potion_type[i] * potion.quantity
        used_ml[i] += potion_ml
        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory
            SET num_{colors[i]}_ml = num_{colors[i]}_ml - :potion_ml
            """), {"potion_ml": potion_ml})    
    global_inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
    print(f"Bottling used (ml): {used_ml}\n"
          f"Current inventory (ml): [{global_inventory.num_red_ml}, {global_inventory.num_green_ml}, " \
          f"{global_inventory.num_blue_ml}, {global_inventory.num_dark_ml}]")
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
    global_inventory = connection.execute(sqlalchemy.text("""
        SELECT SUM(change_gold) as gold, SUM(change_red_ml) as num_red_ml,
               SUM(change_green_ml) as num_green_ml, SUM(change_blue_ml) as num_blue_ml,
               SUM(change_dark_ml) as num_dark_ml
        FROM global_inventory_entries
        """)).first()
    potion_inventory = connection.execute(sqlalchemy.text("""
        SELECT potion_type, num_potion
        FROM potion_inventory
        """)).fetchall()
    current_ml = [global_inventory.num_red_ml, global_inventory.num_green_ml, global_inventory.num_blue_ml, global_inventory.num_dark_ml]
    # splits total_num_bottles to even amounts, tries to even out each color
    current_types = []
    num_bottles = {}
    for potion in potion_inventory:
      num_each = MAX_NUM_EACH - potion.num_potion
      if num_each > 0:
        current_types.append(potion.potion_type)
        num_bottles[tuple(potion.potion_type)] = num_each
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
  return bottling_list
