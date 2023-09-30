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
    print("Delivering Potions:")
    for order in potions_delivered:
        if order.potion_type == [100, 0, 0, 0]: # full red
            count = order.quantity
    
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
                for row in result:
                    current_red = row[1]
                    current_ml = row[2]
                updated_red = current_red + count
                updated_ml = current_ml - count*100
                print(f"{count} red potions delivered, new red mL stock is {updated_ml}, new red potion stock is {updated_red}")
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {updated_red}"))
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {updated_ml}"))

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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            current_ml = row[2]
        max_bottles = current_ml // 100
        result_ml = current_ml - max_bottles*100
        # result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {result_ml}"))
        # result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {max_bottles}"))
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": max_bottles,
            }
        ]
