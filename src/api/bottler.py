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

def deliver_bottles(potions_delivered,num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml):
    for potion in potions_delivered:
        match potion.potion_type:
            case [100,0,0,0]:
                num_red_ml -= potion.quantity * 100
                num_red_potions += potion.quantity
            case [0,100,0,0]:
                num_green_ml -= potion.quantity * 100
                num_green_potions += potion.quantity
            case [0,0,100,0]:
                num_blue_ml -= potion.quantity * 100
                num_blue_potions += potion.quantity
            case _:
                raise Exception("Invalid sku")
    return gold, num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    with db.engine.begin() as connection:
        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()      
        gold, num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml = deliver_bottles(potions_delivered,num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml)
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:num_red_ml,num_green_ml=:num_green_ml,num_blue_ml=:num_blue_ml,num_red_potions=:num_red_potions,num_green_potions=:num_green_potions, num_blue_potions=:num_blue_potions ,gold=:gold"),{"num_red_potions":num_red_potions,"num_red_ml":num_red_ml,"gold":gold,"num_blue_potions":num_blue_potions,"num_blue_ml":num_blue_ml,"num_green_potions":num_green_potions,"num_green_ml":num_green_ml,"gold":gold})
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
        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()
    plan = []
    if num_red_ml > 100:
        plan.append({
            "potion_type": [100, 0, 0, 0],
            "quantity": num_red_ml//100,
        })
    if num_green_ml > 100:
        plan.append({
            "potion_type": [0, 100, 0, 0],
            "quantity": num_green_ml/100,
        })
    if num_blue_ml > 100:
        plan.append({
            "potion_type": [0, 0, 100, 0],
            "quantity": num_blue_ml/100,
        })
    return plan
