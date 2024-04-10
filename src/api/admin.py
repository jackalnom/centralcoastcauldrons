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
    sql_to_execute = f"UPDATE global_inventory SET num_green_potions = 0, num_green_ml = 0, num_red_potions = 0, num_red_ml = 0, num_blue_potions = 0, num_blue_ml = 0, gold = 100"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    sql_to_execute = f"DELETE FROM barrel_purchases"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    sql_to_execute = f"DELETE FROM carts"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

