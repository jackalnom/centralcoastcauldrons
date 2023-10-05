from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
from src.api import database as db
from src.api import colors

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
        color = colors.get_color_from_potion_type(potion.potion_type)
        # will be only red potions for now
        inventory = db.get_global_inventory()
        cur_ml = inventory[f"num_{color}_ml"]
        cur_potions = inventory[f"num_f{color}_potions"]
        new_ml = cur_ml - potion.quantity * 100
        new_potions = cur_potions + potion.quantity

        update_command = f"UPDATE global_inventory SET num_{color}_ml = {new_ml}, num_{color}_potions = {new_potions} WHERE id = 1"
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
    ans = []
    for color in colors.colors:
        ml = inventory[f"num_{color}_ml"]
        potions_to_brew = ml // 100
        if potions_to_brew <= 0:
            print(f"can't brew any {color} potions")
            continue
        ans.append(
            {
                "potion_type": colors.get_base_potion_type(color),
                "quantity": potions_to_brew,
            }
        )

    return ans
