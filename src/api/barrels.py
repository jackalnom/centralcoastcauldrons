from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import re

# GLOBAL regex
barrel_re = re.compile("(\w+)_(\w+)_BARREL")
COLOR_THRESEHOLD = {
    "red": 300,
    "blue": 300,
    "green": 500,
    "dark": 500
}

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

#TODO: create Orders table to keep track of all orders???
@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    mls_delivered = 0 
    total_gold = 0 
    gold = 0
    if (len(barrels_delivered) == 0):
        raise("No barrels sent in API")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT gold 
            FROM global_inventory_temp
        """))
        if (not (gold := result.first()[0])):
            print("Server Error")
            raise("/deliver/{order_id} error with DB")
        
        # check if potion exists???
        for barrel in barrels_delivered:
            print(barrel_re.match(barrel.sku))
            if (barrel.price < 0) or not (match := barrel_re.match(barrel.sku)):
                continue
            # assuming barrel exists
            mls_delivered = (barrel.quantity * barrel.ml_per_barrel)
            cost = barrel.quantity * barrel.price

            if gold < cost:
                print("insufficient gold.")
                continue;

             # update gold
            gold -= cost
            barrel_type = f"{match.group(2)}_ml"
            print(barrel_type)
            # update ML for db
            connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory_temp
            SET {barrel_type} = {barrel_type} + {mls_delivered}  
            """))
            print("Recieved: ", barrel_type, " AMOUNT: ", mls_delivered)

        # update gold that was recieved

        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory_temp
            SET gold = {gold}
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
    num_potion_re = re.compile("((?:\w+\s+)+)(?=potions?)")
    # keept track of what we want to purchase
    purchased = []
    # buy BARRELS of any color when we are short of said color and have sufficient money
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT gold, red_ml AS red, green_ml AS green, blue_ml AS blue, dark_ml AS dark
            FROM global_inventory_temp
        """))
        map = result.mappings().first()

        # iterate through keys looking for all available colors
        inventory = dict(map.items())
        print(inventory)
        gold = inventory["gold"]
        # check respective barrels and how much they have
        # iterate throug barrel catalog, see if we need any of those colors
        for barrel in wholesale_catalog:
            # get the color of the barrel
            barrel_match = barrel_re.match(barrel.sku)
            if(not barrel_match):
                print(barrel.sku)
                continue
            size = barrel_match.group(1)
            color = barrel_match.group(2).lower()
            # check if the number of ml we want for a given color is less than thresehold
            if (inventory[color] < COLOR_THRESEHOLD.get(color, 0)):
                # purchase barrel
                if (barrel.price < gold and size.lower() != "mini"):
                    gold -= barrel.price
                    print(f"purchased {barrel.sku} at {barrel.price}")
                    purchased.append(
                        {
                            "sku": barrel.sku,
                            "quantity" : 1
                        }
                    )
                    # add to "demo" inventory
                    inventory[color] += barrel.ml_per_barrel
                else:
                    print("Insufficient gold", barrel, gold)
                    continue;

    print(wholesale_catalog)
    return purchased


