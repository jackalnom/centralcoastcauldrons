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
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, potion_capacity FROM global_inventory"))
    ml_row = result.fetchone()

    capacity = ml_row[4]

    red_ml = ml_row[0]
    green_ml = ml_row[1]
    blue_ml = ml_row[2]
    dark_ml = ml_row[3]

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT parts_red, parts_green, parts_blue, parts_dark, num_potions
                                                    FROM potions 
                                                    ORDER BY priority ASC"""))
    potion_row_list = result.all()

    print("potion_row_list: ", potion_row_list)

    available_space = capacity
    for row in potion_row_list:
        available_space -= row[4]

    # idea: I want to prioritize making special potions firs
    temp_bottle_plan = []
    for i in range(len(potion_row_list)):
        temp_bottle_plan.append(0)

    again = True
    while available_space > 0 and again == True:
        again = False
        for i in range(len(potion_row_list)):
            if red_ml >= potion_row_list[i][0] and green_ml >= potion_row_list[i][1] and blue_ml >= potion_row_list[i][2] and dark_ml >= potion_row_list[i][3]:
                temp_bottle_plan[i] += 1

                red_ml -= potion_row_list[i][0]
                green_ml -= potion_row_list[i][1]
                blue_ml -= potion_row_list[i][2]
                dark_ml -= potion_row_list[i][3]

                available_space -= 1
                again = True
    
    bottle_plan = []
    for i in range(len(potion_row_list)):
        if temp_bottle_plan[i] > 0:
            bottle_plan.append({"potion_type": [potion_row_list[i][0], potion_row_list[i][1], potion_row_list[i][2], potion_row_list[i][3]], "quantity": temp_bottle_plan[i]})

    print("temp_bottle_plan: ", temp_bottle_plan) 
    print("bottle_plan: ", bottle_plan)
    return bottle_plan


if __name__ == "__main__":
    print(get_bottle_plan())