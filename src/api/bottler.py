from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
from src.api import database as db

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
    for potion in potions_delivered:
        # will be only red potions for now
        inventory = db.get_global_inventory()
        cur_red_ml = inventory["num_red_ml"]
        cur_red_potions = inventory["num_red_potions"]
        new_red_ml = cur_red_ml - potion.quantity * 100
        new_red_potions = cur_red_potions + potion.quantity

        update_command = f"UPDATE global_inventory SET num_red_ml = {new_red_ml}, num_red_potions = {new_red_potions} WHERE id = 1"
        db.execute(update_command)
    print(potions_delivered)

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
    inventory = db.get_global_inventory()
    red_ml = inventory["num_red_ml"]
    potions_to_brew = red_ml // 100
    if potions_to_brew <= 0:
        print("can't brew any potions")
        return

    return [
        {
            "potion_type": [100, 0, 0, 0],
            "quantity": potions_to_brew,
        }
    ]
