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

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    delivery_dict = {
        0: "red",
        1: "green",
        2: "blue"
    }
    print("Delivering Potions:")
    for order in potions_delivered:
        color = delivery_dict[order.potion_type.index(100)] # still assuming pure potions
        count = order.quantity

        # oull and update potion delivery
        with db.engine.begin() as connection:
            result_ml = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
            result_potion = connection.execute(sqlalchemy.text(f"SELECT num_{color}_potions FROM global_inventory"))
        for row in result_potion:
            current_potion = row[0]
        for row in result_ml:
            current_ml = row[0]
        updated_potion = current_potion + count
        updated_ml = current_ml - count*100
        print(f"{count} {color} potions delivered, new {color} mL stock is {updated_ml}, new {color} potion stock is {updated_potion}")
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_potions = {updated_ml}"))
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_ml = {updated_ml}"))
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
    response = []
    colors_list = ["red", "green", "blue"]
    potion_type_dict = {
        "red":[100,0,0,0],
        "green":[0,100,0,0],
        "blue":[0,0,100,0]
    }
    # Initial logic: bottle all barrels into red potions.
    for color in colors_list:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
        for row in result:
            current_ml = row[0]
        max_bottles = current_ml // 100
        result_ml = current_ml - max_bottles*100
        # result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {result_ml}"))
        # result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {max_bottles}"))
        print(f"Plan produces {max_bottles} {color} potions...")
        response += [
                {
                    "potion_type": potion_type_dict[color],
                    "quantity": max_bottles,
                }
            ]
