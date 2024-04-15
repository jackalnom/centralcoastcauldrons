from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    print("CALLED post_deliver_bottles()")
    red_deduction = red_amount = green_deduction = green_amount = blue_deduction = blue_amount = 0
    for potion in potions_delivered:
        potion_type = potion.potion_type
        amount = potion.quantity

        # check if red potion
        if potion_type == [100, 0, 0, 0]:
            red_deduction += 100 * amount
            red_amount += amount
        # check if green potion
        elif potion_type == [0, 100, 0, 0]:
            green_deduction += 100 * amount
            green_amount += amount
        # check if blue potion
        elif potion_type == [0, 0, 100, 0]:
            blue_deduction += 100 * amount
            blue_amount += amount

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = num_red_potions + {red_amount}, num_red_ml = num_red_ml - {red_deduction}, num_green_potions = num_green_potions + {green_amount}, num_green_ml = num_green_ml - {green_deduction}, num_blue_potions = num_blue_potions + {blue_amount}, num_blue_ml = num_blue_ml - {blue_deduction}"))

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    print("CALLED get_bottle_plan()")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_red_ml, num_blue_ml FROM global_inventory"))
    row = result.fetchone()
    num_green_bottles = row[0] // 100
    num_red_bottles = row[1] // 100
    num_blue_bottles = row[2] // 100

    print(f"num red bottles: {num_red_bottles}, num green bottles: {num_green_bottles}, num blue bottles: {num_blue_bottles}")

    bottle_plan = []
    if num_green_bottles > 0:
        bottle_plan.append({
            "potion_type": [0, 100, 0, 0],
            "quantity": num_green_bottles,
        })
    if num_red_bottles > 0:
        bottle_plan.append({
            "potion_type": [100, 0, 0, 0],
            "quantity": num_red_bottles,
        })
    if num_blue_bottles > 0:
        bottle_plan.append({
            "potion_type": [0, 0, 100, 0],
            "quantity": num_blue_bottles,
        })


    print("bottle_plan: ", bottle_plan)
    return bottle_plan


if __name__ == "__main__":
    print(get_bottle_plan())