from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

colors = ["red", "green", "blue"]
color_to_potion = {
    "red": [100, 0, 0, 0],
    "green": [0, 100, 0, 0],
    "blue": [0, 0, 100, 0],
}
color_to_price = {
    "red": 75,
    "green": 75,
    "blue": 100,
}

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
  """
  Each unique item combination must have only a single price.
  """

  # Can return a max of 20 items.
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    first_row = result.first()
    catalog = []
    for color in colors:
      current_potions = getattr(first_row, f"num_{color}_potions")
      if current_potions != 0:
        catalog.append({
          "sku": f"{color.upper()}_POTION_0",
          "name": f"{color} potion",
          "quantity": current_potions if current_potions <= 10000 else 10000,
          "price": color_to_price[color],
          "potion_type": color_to_potion[color],
        })
  return catalog