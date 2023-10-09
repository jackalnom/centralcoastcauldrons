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
    # for logging
    total_barrels_cost = 0
    added_ml = {color: 0 for color in colors}
    for barrel in barrels_delivered:
      color = potion_to_color[tuple(barrel.potion_type)]
      barrels_cost = barrel.price * barrel.quantity
      barrels_ml = barrel.ml_per_barrel * barrel.quantity
      total_barrels_cost += barrels_cost
      added_ml[color] += barrels_ml
      # update gold and number of ml in global_inventory
      connection.execute(sqlalchemy.text(f"""
          UPDATE global_inventory
          SET gold = gold - :barrels_cost,
            num_{color}_ml = num_{color}_ml + :barrels_ml
          """), {"barrels_cost": barrels_cost, "barrels_ml": barrels_ml})
    global_inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
    print(f"Barreling added (ml): [{added_ml['red']}, {added_ml['green']}, {added_ml['blue']}, {added_ml['dark']}]\n" \
          f"Barreling used (gold): {total_barrels_cost}\n" \
          f"Current inventory (ml, gold): [{global_inventory.num_red_ml}, {global_inventory.num_green_ml}, " \
          f"{global_inventory.num_blue_ml}, {global_inventory.num_dark_ml}], {global_inventory.gold}")
  return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
  """ """
  print(wholesale_catalog)
  buying_barrels = []
  with db.engine.begin() as connection:
    global_inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
    potion_inventory = connection.execute(sqlalchemy.text("""
        SELECT potion_type, num_potion
        FROM potion_inventory
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
              if buying_barrel["sku"] == barrel.sku:
                if buying_barrel["quantity"] + 1 < barrel.quantity:
                  buying_barrel["quantity"] += 1
          bought = True
          current_gold -= barrel.price
          current_ml[color_index] += barrel.ml_per_barrel
          break
      # ran out of color
      if not bought:
        current_ml.pop(color_index)
  return buying_barrels
