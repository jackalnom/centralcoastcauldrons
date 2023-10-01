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

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
  """ """
  print(barrels_delivered)
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    current_gold = first_row.gold
    current_num_red_ml = first_row.num_red_ml
    for barrel in barrels_delivered:
      if barrel.sku == 'SMALL_RED_BARREL':
        current_gold -= barrel.price * barrel.quantity
        current_num_red_ml += barrel.ml_per_barrel * barrel.quantity
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold={current_gold}, num_red_ml={current_num_red_ml}"))
  
  return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
  """ """
  print(wholesale_catalog)
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    for barrel in wholesale_catalog:
      if barrel.sku == 'SMALL_RED_BARREL' and first_row.num_red_potions < 10 and first_row.gold >= barrel.price:
        return [
          {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
          }
        ]
  return []
