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
    connection.execute(sqlalchemy.text("TRUNCATE global_inventory_transactions CASCADE"))
    transaction_id = connection.execute(sqlalchemy.text("INSERT INTO global_inventory_transactions DEFAULT VALUES RETURNING id")).first().id
    connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_entries (global_inventory_transaction_id)
        VALUES (:transaction_id)
        """), {"transaction_id": transaction_id})
  return "OK"


@router.get("/shop_info/")
def get_shop_info():
  """ """

  # TODO: Change me!
  return {
      "shop_name": "phun potions",
      "shop_owner": "Dennis Phun",
  }
