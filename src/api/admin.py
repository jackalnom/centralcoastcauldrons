from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src.api import database as db
from src.api import colors as colorUtils

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
    colors = colorUtils.colors
    update_command = "UPDATE global_inventory SET"
    for color in colors:
        update_command += f" SET num_{color}_potions = 0, num_{color}_ml = 0"
    update_command += "SET gold = 100"
    db.execute(update_command)
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Potions by Gucci",
        "shop_owner": "Alex Buchko",
    }
