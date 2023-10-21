from fastapi import APIRouter
import sqlalchemy
from src import database as db
from datetime import datetime


router = APIRouter()


convert_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
  """
  Each unique item combination must have only a single price.
  """

  # Can return a max of 20 items.
  with db.engine.begin() as connection:
    day = convert_days[datetime.now().weekday()]
    potion_inventory = connection.execute(sqlalchemy.text(f"""
        SELECT potions.sku, potions.{day}_price as price, potions.potion_type, COALESCE(SUM(change), 0) as num_potion
        FROM potions
        LEFT JOIN potion_entries ON potion_entries.potion_sku = potions.sku                      
        GROUP BY potions.sku, potions.{day}_price, potions.potion_type
        ORDER BY {day}_sold DESC, random()
        """)).fetchall()
    catalog = []
    for potion in potion_inventory:
      if len(catalog) < 6 and potion.num_potion != 0:
        catalog.append({
          "sku": potion.sku,
          "name": potion.sku,
          "quantity": potion.num_potion if potion.num_potion <= 10000 else 10000,
          "price": potion.price,
          "potion_type": potion.potion_type,
        })
  return catalog
