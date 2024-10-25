import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

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

    #reset values when shop is burned to the ground
        #ml and potions 0
        #gold 100
    with db.engine.begin() as connection:

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions, num_green_potions, num_blue_potions = 0"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml, num_green_ml, num_blue_ml = 0"))
  
    return "OK"

