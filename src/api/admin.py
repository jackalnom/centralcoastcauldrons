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
    potion_reset_sql = "DELETE FROM potions"
    barrel_reset_sql = "DELETE FROM barrels"
    gold_reset_sql = "DELETE FROM gold_ledger"
    carts_sql = f"DELETE FROM carts"
    cart_items_sql = f"DELETE FROM cart_items"
    starting_gold_sql = "INSERT INTO gold_ledger (order_id, gold) VALUES (-1, 100)"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(potion_reset_sql))
        connection.execute(sqlalchemy.text(barrel_reset_sql))
        connection.execute(sqlalchemy.text(gold_reset_sql))
        connection.execute(sqlalchemy.text(carts_sql))
        connection.execute(sqlalchemy.text(cart_items_sql))
        connection.execute(sqlalchemy.text(starting_gold_sql))
    return "OK"

