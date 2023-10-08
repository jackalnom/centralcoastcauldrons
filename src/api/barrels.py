from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from ..colors import colors, color_to_potion


router = APIRouter(
  prefix="/barrels",
  tags=["barrels"],
  dependencies=[Depends(auth.get_api_key)],
)


potion_to_color = {
  (1, 0, 0, 0): "red",
  (0, 1, 0, 0): "green",
  (0, 0, 1, 0): "blue",
  (0, 0, 0, 1): "dark"
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
    added_ml = {"red": 0, "green": 0, "blue": 0, "dark": 0}
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
    while current_gold > 1000 and len(buying_barrels) != len(wholesale_catalog):
      split_gold = current_gold / len(colors)
      for color in colors:
        for barrel in wholesale_catalog:
          if barrel.potion_type == color_to_potion[color] and split_gold >= barrel.price and \
              not any(buying_barrel["sku"] == barrel.sku for buying_barrel in buying_barrels):
            num_buying = int(split_gold // barrel.price)
            num_buying = num_buying if num_buying <= barrel.quantity else barrel.quantity
            buying_barrels.append({
              "sku": barrel.sku,
              "quantity": num_buying,
            })
            current_gold -= num_buying * barrel.price
            break
    for barrel in wholesale_catalog:
      if current_gold >= barrel.price:
        num_buying = current_gold // barrel.price
        num_buying = num_buying if num_buying <= barrel.quantity else barrel.quantity
        for buying_barrel in buying_barrels:
          if buying_barrel["sku"] == barrel.sku:
            if buying_barrel["quantity"] + num_buying < barrel.quantity:
              buying_barrel["quantity"] += num_buying
            return buying_barrels
        buying_barrels.append({
          "sku": barrel.sku,
          "quantity": num_buying
        })
        break
  return buying_barrels
