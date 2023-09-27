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
    clear_inventory_sql = sqlalchemy.text(
        "update global_inventory set num_red_ml = 0, num_red_potions = 0 , gold = 100")
    print("clear_inventory_sql: ", clear_inventory_sql)
    clear_carts_sql = sqlalchemy.text("delete from global_carts")
    print("clear_carts_sql: ", clear_carts_sql)
    with db.engine.begin() as connection:
        connection.execute(clear_inventory_sql)
        print("Executed clear_inventory_sql")
        connection.execute(clear_carts_sql)
        print("Executed clear_carts_sql")
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    return {
        "shop_name": "Best Triple C",
        "shop_owner": "The Potion Salesman",
    }

