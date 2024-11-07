import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

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
    """Deliver bottles!"""
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        #set the base colors needed to 0
        total_red_needed = 0
        total_green_needed = 0
        total_blue_needed = 0
        total_dark_needed = 0

        counter = 0

        #potions_delivered is a list of PotionInventory objects, PotionInventory has a list of int
        for potion in potions_delivered:
            #select the amounts of red, green, blue, and dark needed for the specific potion
            potion_data = connection.execute(sqlalchemy.text(f"""SELECT red_amt, green_amt, blue_amt, dark_amt 
                                                        FROM potion_mixes 
                                                        WHERE id = {potion.potion_type[counter]}""")).fetchone()
            counter + 1

            #if the potion data is not valid, error message
            if not potion_data:
                print(f"ERROR: Not a valid potion mixture ID: {potion.potion_type}")
                return "ERROR! potion data not valid"
            #put the recipe in potion_data
            red_amt, green_amt, blue_amt, dark_amt = potion_data

            #must have 100 ml per potion
            required_ml = potion.quantity * 100

            #add the total ml needed for each base color
            total_red_needed += red_amt * required_ml
            total_green_needed += green_amt * required_ml
            total_blue_needed += blue_amt * required_ml
            total_dark_needed += dark_amt * required_ml

        #select the available mls from inventory
        check_ml_sql = "SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory"
        ml_inventory = connection.execute(sqlalchemy.text(check_ml_sql)).fetchone()

        #if there is not enough mls of each color required for the specific potion type, error message
        if(ml_inventory[0] < total_red_needed 
           or ml_inventory[1] < total_green_needed 
           or ml_inventory[2] < total_blue_needed 
           or ml_inventory[3] < total_dark_needed):
            print(f"ERROR: Not enough ml to make {potion.quantity} of potion {potion.potion_type}")
            return "ERROR! not enough ml"
        
        #otherwise, update the inventory because you have enough ml to go through with the bottling
        update_inventory_sql = f"""UPDATE global_inventory 
            SET num_red_ml = num_red_ml - {red_amt * required_ml}, 
            num_green_ml = num_green_ml - {green_amt * required_ml}, 
            num_blue_ml = num_blue_ml - {blue_amt * required_ml}, 
            num_dark_ml = num_dark_ml - {dark_amt * required_ml}"""
        connection.execute(sqlalchemy.text(update_inventory_sql))

        #update quantity of the special types
        update_potion_mix_inventory_sql = f"""UPDATE potion_mixes
                                        SET inventory = inventory + {potion.potion.quantity}
                                        WHERE id = {potion.potion_type}"""
        connection.execute(sqlalchemy.text(update_potion_mix_inventory_sql))
        
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    #collect current amount of ml of each base color
    redmlqry = "SELECT SUM(num_red_ml) AS current_red_ml FROM ml_ledgers"
    greenmlqry = "SELECT SUM(num_green_ml) AS current_green_ml FROM ml_ledgers"
    bluemlqry = "SELECT SUM(num_blue_ml) AS current_blue_ml FROM ml_ledgers"
    darkmlqry = "SELECT SUM(num_dark_ml) AS current_dark_ml FROM ml_ledgers"

    #list to hold plan of (multiple) potion(s)
    potion_plan = []

    with db.engine.begin() as connection:
        redml = connection.execute(sqlalchemy.text(redmlqry)).scalar()
        greenml = connection.execute(sqlalchemy.text(greenmlqry)).scalar()
        blueml = connection.execute(sqlalchemy.text(bluemlqry)).scalar()
        darkml = connection.execute(sqlalchemy.text(darkmlqry)).scalar()

        print(f"""redml: {redml} greenml: {greenml} blueml: {blueml} darkml: {darkml}""")

        #if there is enough base color ml, add to potion recipe plan
        if(redml >= 100): #red potion
            potion_plan.append([{"potion_type": [100, 0, 0, 0]}])
        
        if(greenml >= 100): #green potion
            potion_plan.append([{"potion_type": [0, 100, 0, 0]}])
        
        if(blueml >= 100): #blue potion
            potion_plan.append([{"potion_type": [0, 0, 100, 0]}])
        
        if(darkml >= 100): #dark potion
            potion_plan.append([{"potion_type": [0, 0, 0, 100]}])
        
        #if there is enough special potions, add to plan
        if(blueml >= 50 and redml >= 50): #purple potion
            potion_plan.append([{"potion_type": [50, 0, 50, 0]}])

        if(blueml >= 50 and greenml >= 50): #teal potion
            potion_plan.append([{"potion_type": [0, 50, 50, 0]}])

        if(redml >= 25 and greenml >= 25 and blueml >= 25 and darkml >= 25): #slo special potion
            potion_plan.append([{"potion_type": [25, 25, 25, 25]}])
        
        if potion_plan:
            return potion_plan
        else:
            return "Not enough ml to make a single bottle! :()"

if __name__ == "__main__":
    print(get_bottle_plan())