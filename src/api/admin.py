from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src.api import database as db

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
    update_command = "UPDATE global_inventory SET num_red_potions = 0, num_red_ml = 0, gold = 100 WHERE id = 1"
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
