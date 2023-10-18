from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api.database import engine as db
from src.api.models import Inventory, PotionsInventory

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

def deliver_bottles(potions_delivered,gold, num_red_ml,num_blue_ml,num_green_ml, potions):
    pd = []

    for potion in potions_delivered:
        for potion_entry in potions:
            if potion_entry[1] == potion.potion_type:
                # potion_entry.quantity += potion.quantity
                num_red_ml -= potion.potion_type[0] * potion.quantity
                num_green_ml -= potion.potion_type[1] * potion.quantity
                num_blue_ml -= potion.potion_type[2] * potion.quantity
                pd.append([potion_entry, potion.quantity])
                break
    return gold, num_red_ml,num_blue_ml,num_green_ml, pd


@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    potions = PotionsInventory(db.engine)
    potion_entries = potions.get_inventory()
    gold,red,blue,green,pd = deliver_bottles(potions_delivered,*inventory.get_inventory(), potion_entries)
    print(potions_delivered)
    for potion in pd:
        potions.update_quantity(potion[0][1], potions.get_entry(potion[0][1])[2] + potion[1])
    inventory.set_inventory(gold,red,blue,green)
    inventory.sync()
    return "OK"


def bottle_plan(gold,num_red_ml,num_blue_ml,num_green_ml,potion_entries):
    """
    Go from barrel to bottle.
    """

    plan = []

    for potion_entry in potion_entries:
        print(potion_entry)
        if num_red_ml >= potion_entry[1][0] and num_green_ml >= potion_entry[1][1] and num_blue_ml >= potion_entry[1][2]:
            plan.append(
                {"potion_type":potion_entry[1], 
                 "quantity": 
                 num_red_ml//potion_entry[1][0] if potion_entry[1][0] != 0 else 0 or  
                 num_green_ml//potion_entry[1][1] if potion_entry[1][1] != 0 else 0 or
                 num_blue_ml//potion_entry[1][2] if potion_entry[1][2] != 0 else 0})
            num_red_ml -= potion_entry[1][0] * plan[-1]["quantity"] * potion_entry[1][0]
            num_green_ml -= potion_entry[1][1] * plan[-1]["quantity"] * potion_entry[1][1]
            num_blue_ml -= potion_entry[1][2] * plan[-1]["quantity"] * potion_entry[1][2]
    print(plan)
    return plan

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
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    print(inventory.get_inventory())
    potions = PotionsInventory(db.engine)
    plan = bottle_plan(*inventory.get_inventory(),potions.get_inventory())
    print("plan",plan)
    return plan
