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
    print("Burning shop to the ground...")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"DELETE FROM global_inventory"))
        result = connection.execute(sqlalchemy.text(f"INSERT INTO global_inventory DEFAULT VALUES"))
        result = connection.execute(sqlalchemy.text(f"DELETE FROM potion_inventory"))
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Potionality",
        "shop_owner": "Matthew Wong",
    }

