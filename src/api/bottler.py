import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.api.audit import get_inventory
from src import database as db

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
    inventory = get_inventory()
    num_potions_to_brew = inventory["ml_in_barrels"] // 100
    sql_to_execute = sqlalchemy.text(
        "update global_inventory set num_red_ml = num_red_ml - {0}, num_red_potions = num_red_potions + {1} "
        .format(num_potions_to_brew * 100, num_potions_to_brew))
    with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
    return [
        {
            "potion_type": [100, 0, 0, 0],
            "quantity": num_potions_to_brew,
        }
    ]
