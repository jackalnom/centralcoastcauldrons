from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime


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
    used_ml = [0, 0, 0, 0]
    for potion in potions_delivered:
      # update potion_inventory
      potion_transaction_id = connection.execute(sqlalchemy.text("""
        INSERT INTO potion_transactions (description)
        VALUES (:description)
        RETURNING id
        """), {"description": "Bottled: " + str(potion)}).first().id
      connection.execute(sqlalchemy.text("""
        INSERT INTO potion_entries (potion_sku, change, potion_transaction_id)
        SELECT potions.sku, :change, :transaction_id
        FROM potions WHERE potions.potion_type = :potion_type
        """), {"change": potion.quantity, "transaction_id": potion_transaction_id, "potion_type": potion.potion_type})
      for i in range(len(colors)):
        potion_ml = potion.potion_type[i] * potion.quantity
        used_ml[i] += potion_ml
    # update global_inventory
    global_transaction_id = connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_transactions (description)
        VALUES (:description)
        RETURNING id
        """), {"description": "Bottled: " + str(potions_delivered)}).first().id
    connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_entries
          (change_gold, change_red_ml, change_green_ml, change_blue_ml, change_dark_ml, global_inventory_transaction_id)
        VALUES (:gold, :num_red_ml, :num_green_ml, :num_blue_ml, :num_dark_ml, :transaction_id)
        """), {"gold": 0, "num_red_ml": -used_ml[0], "num_green_ml": -used_ml[1],
              "num_blue_ml": -used_ml[2], "num_dark_ml": -used_ml[3], "transaction_id": global_transaction_id})
  return "OK"


convert_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


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
  day = convert_days[datetime.now().weekday()]
  with db.engine.begin() as connection:
    global_inventory = connection.execute(sqlalchemy.text("""
        SELECT SUM(change_gold) as gold, SUM(change_red_ml) as num_red_ml,
               SUM(change_green_ml) as num_green_ml, SUM(change_blue_ml) as num_blue_ml,
               SUM(change_dark_ml) as num_dark_ml
        FROM global_inventory_entries
        """)).first()
    potion_inventory = connection.execute(sqlalchemy.text(f"""
        SELECT potions.potion_type, COALESCE(SUM(change), 0) as num_potion
        FROM potions
        LEFT JOIN potion_entries ON potion_entries.potion_sku = potions.sku                      
        GROUP BY {day}_sold, potions.potion_type
        ORDER BY {day}_sold DESC, random()
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
