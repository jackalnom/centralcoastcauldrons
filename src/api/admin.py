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
    potion_catalog_sql = f"UPDATE potion_catalog_items SET quantity = 0"
    barrels_sql = f"UPDATE barrel_inventory SET potion_ml = 0"
    carts_sql = f"DELETE FROM carts"
    cart_items_sql = f"DELETE FROM cart_items"
    global_inventory_sql = f"UPDATE global_inventory SET gold = 100, cart_id = 0"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(potion_catalog_sql))
        connection.execute(sqlalchemy.text(barrels_sql))
        connection.execute(sqlalchemy.text(carts_sql))
        connection.execute(sqlalchemy.text(cart_items_sql))
        connection.execute(sqlalchemy.text(global_inventory_sql))
    return "OK"

