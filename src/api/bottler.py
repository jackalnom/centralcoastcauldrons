import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src import database as db
from src.api import auth
from src.api.audit import get_inventory

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
    red_potions_delivered = list(filter(lambda potion: potion.potion_type == [100, 0, 0, 0], potions_delivered))
    print("red_potions_delivered:", red_potions_delivered)
    if red_potions_delivered:
        num_red_potions_delivered = red_potions_delivered[0].quantity
        update_potion_inventory_sql = sqlalchemy.text(
            "update global_inventory set num_red_potions = num_red_potions + {0}, num_red_ml = num_red_ml - {1}".format(num_red_potions_delivered, num_red_potions_delivered * 100))
        print("update_potion_inventory_sql", update_potion_inventory_sql)
        with db.engine.begin() as connection:
            connection.execute(update_potion_inventory_sql)
            print("Executed update_potion_inventory_sql")
    else:
        print("No red potions delivered")

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
    print("inventory:", inventory)
    num_potions_to_brew = inventory["ml_in_barrels"] // 100
    print("num_potions_to_brew:", num_potions_to_brew)
    payload = [
        {
            "potion_type": [100, 0, 0, 0],
            "quantity": num_potions_to_brew,
        }
    ]
    print(payload)
    return payload
