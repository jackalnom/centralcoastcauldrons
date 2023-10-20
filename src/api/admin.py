from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
  prefix="/admin",
  tags=["admin"],
  dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset")
def reset():
  """
  Reset the game state. Gold goes to 100, all potions are removed from
  inventory, and all barrels are removed from inventory. Carts are all reset.
  """
  with db.engine.begin() as connection:
    connection.execute(sqlalchemy.text("TRUNCATE global_inventory"))
    connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory
        (change_gold, change_red_ml, change_green_ml, change_blue_ml, change_dark_ml, description)
        VALUES (100, 0, 0, 0, 0, 'Starting inventory')
        """))
  return "OK"


@router.get("/shop_info/")
def get_shop_info():
  """ """

  # TODO: Change me!
  return {
      "shop_name": "phun potions",
      "shop_owner": "Dennis Phun",
  }
