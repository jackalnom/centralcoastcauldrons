from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api.database import engine as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    for potion in potions_delivered:
        if potion.potion_type != [100, 0, 0, 0]:
            return "INVALID POTION TYPE"
        
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            num_red_potions, num_red_ml, _= result.fetchone()

            for potion in potions_delivered:
                num_red_ml -= potion.quantity
                num_red_potions += potion.quantity
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        _, num_red_ml, _= result.fetchone()

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_ml,
            }
        ]
