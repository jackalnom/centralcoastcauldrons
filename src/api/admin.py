from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

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
        sql_to_execute = sqlalchemy.text("update global_inventory set num_red_ml = 0, num_red_potions = 0 , gold = 100")
        connection.execute(sql_to_execute)
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    return {
        "shop_name": "Best Triple C",
        "shop_owner": "The Potion Salesman",
    }

