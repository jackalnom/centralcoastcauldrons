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

colors = ["red", "green", "blue", "dark"]

potion_to_color = {
  (1, 0, 0, 0): "red",
  (0, 1, 0, 0): "green",
  (0, 0, 1, 0): "blue",
  (0, 0, 0, 1): "dark"
}

color_to_potion = {
  "red": [1, 0, 0, 0],
  "green": [0, 1, 0, 0],
  "blue": [0, 0, 1, 0],
  "dark": [0, 0, 0, 1]
}


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
    total_barrels_cost = 0
    added_ml = {color: 0 for color in colors}
    for barrel in barrels_delivered:
      color = potion_to_color[tuple(barrel.potion_type)]
      barrels_cost = barrel.price * barrel.quantity
      barrels_ml = barrel.ml_per_barrel * barrel.quantity
      total_barrels_cost += barrels_cost
      added_ml[color] += barrels_ml
    # update global_inventory
    transaction_id = connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_transactions (description)
        VALUES (:description)
        RETURNING id
        """), {"description": "Barreled: " + str(barrels_delivered)}).first().id
    connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_entries
          (change_gold, change_red_ml, change_green_ml, change_blue_ml, change_dark_ml, global_inventory_transaction_id)
        VALUES (:barrels_cost, :num_red_ml, :num_green_ml, :num_blue_ml, :num_dark_ml, :transaction_id)
        """), {"barrels_cost": -total_barrels_cost, "num_red_ml": added_ml["red"], "num_green_ml": added_ml["green"], 
               "num_blue_ml": added_ml["blue"], "num_dark_ml": added_ml["dark"], "transaction_id": transaction_id})
  return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
  """ """
  print(wholesale_catalog)
  buying_barrels = []
  with db.engine.begin() as connection:
    global_inventory = connection.execute(sqlalchemy.text("""
        SELECT
          SUM(change_gold) as gold, SUM(change_red_ml) as num_red_ml,
          SUM(change_green_ml) as num_green_ml, SUM(change_blue_ml) as num_blue_ml,
          SUM(change_dark_ml) as num_dark_ml
        FROM global_inventory_entries
        """)).first()
    potion_inventory = connection.execute(sqlalchemy.text("""
        SELECT potions.potion_type, COALESCE(SUM(change), 0) as num_potion
        FROM potions
        LEFT JOIN potion_entries ON potion_entries.potion_sku = potions.sku                      
        GROUP BY potions.potion_type
        """)).fetchall()
    current_gold = global_inventory.gold
    current_ml = [global_inventory.num_red_ml, global_inventory.num_green_ml, global_inventory.num_blue_ml, global_inventory.num_dark_ml]
    for potion in potion_inventory:
      for i in range(4):
        current_ml[i] += potion.potion_type[i] * potion.num_potion
    min_price = min(barrel.price for barrel in wholesale_catalog)
    while current_gold >= min_price and len(buying_barrels) < len(wholesale_catalog):
      bought = False
      color_index = current_ml.index(min(current_ml))
      priority_color = colors[color_index]
      # loops through every barrel, assumes larger barrels comes first
      for barrel in wholesale_catalog:
        # if right color and can buy
        if barrel.potion_type == color_to_potion[priority_color] and current_gold >= barrel.price:
          # add to buying_barrels if not already in
          if not any(buying_barrel["sku"] == barrel.sku for buying_barrel in buying_barrels):
            buying_barrels.append({
              "sku": barrel.sku,
              "quantity": 1,
            })
          # if already in, increment quantity
          else:
            for buying_barrel in buying_barrels:
              if buying_barrel["sku"] == barrel.sku and buying_barrel["quantity"] < barrel.quantity:
                buying_barrel["quantity"] += 1
          bought = True
          current_gold -= barrel.price
          current_ml[color_index] += barrel.ml_per_barrel
          break
      # ran out of color
      if not bought:
        current_ml.pop(color_index)
  return buying_barrels
