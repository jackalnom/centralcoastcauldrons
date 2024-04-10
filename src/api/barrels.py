from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import re

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    mls_delivered = 0 
    total_gold = 0 
    gold = 0
    barrel_re = re.compile("(w+)_(w+)_BARREL")
    if (len(barrels_delivered) == 0):
        raise("No barrels sent in API")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT gold 
            FROM global_inventory
            WHERE id = 1
        """))
        if (not (gold := result.first()[0])):
            print("Server Error")
            raise("/deliver/{order_id} error with DB")
        
        # check if potion exists???
        for barrel in barrels_delivered:
            if (barrel.price < 0) or not (match := barrel_re.match(barrel.sku)):
                continue
            # assuming barrel exists
            mls_delivered = (barrel.quantity * barrel.ml_per_barrel)
            cost = barrel.quantity * barrel.price

            if gold < cost:
                print("insufficient gold.")
                return "NOPE"

             # update gold
            gold -= cost
            barrel_type = f"num_{match.group(2)}_ml"
            print(barrel_type)
            # update ML for db
            connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory
            SET {barrel_type} = {barrel_type} + {mls_delivered}  
            WHERE id = 1
            """))
            print("Recieved: ", barrel_type, " AMOUNT: ", mls_delivered)

        # update gold that was recieved

        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory 
            gold = {gold}
            WHERE id = 1
        """))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    # keep track of ml and potion count for each color
    color_potions = 0
    inventory = {}
    gold = 0

    # simple regex to get all available potions
    num_potion_re = re.compile("num_(\w+)_potions")
    # keept track of what we want to purchase
    purchased = []
    # buy BARRELS of any color when we are short of said color and have sufficient money
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_red_potions, num_green_potions, num_blue_potions, gold 
            FROM global_inventory
            WHERE id = 1
        """))
        inventory = result.mappings().first()

        # iterate through keys looking for all available colors
        gold = inventory["gold"]
        for key in inventory.keys():
            if (color := num_potion_re.match(key)):
                color_potions = inventory[color.string]
                color = color.group(1)
                if (color_potions < 10):
                    # find corresponding color barrel
                    # TODO: use regex and search dictionary instead of having a double for loop <- one search over many
                    # TODO: explore different types of sizing for barrels
                    print( f"SMALL_{color.upper()}_BARREL")
                    for barrel in wholesale_catalog:
                        if barrel.sku == f"SMALL_{color.upper()}_BARREL" and \
                            barrel.quantity >= 1:
                            
                            # get price and purhcase 1 if we have enough
                            price = barrel.price
                            if (gold < price):
                                print("Insufficient gold.")
                                break;
                    
                            print(f"purchased {color} barrel")
                            # update gold to reflect this
                            gold -= price
                            purchased.append(
                            {
                                "sku": f"SMALL_{color.upper()}_BARREL",
                                "quantity" : 1
                            }
                            )
                        
    print(wholesale_catalog)
    return purchased


