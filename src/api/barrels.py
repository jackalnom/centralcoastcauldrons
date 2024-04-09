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
    if (len(barrels_delivered) == 0):
        raise("No barrels sent in API")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT gold 
            FROM global_inventory
            WHERE id = 1
        """))
        if (not (result := result.first())):
            print("Server Error")
            raise("/deliver/{order_id} error with DB")
        
        # check if we have sufficient mls to send
        for barrel in barrels_delivered:
            if (barrel.price < 0) or barrel.potion_type != [0, 100, 0, 0]:
                continue
            mls_delivered += barrel.quantity * barrel.ml_per_barrel
            total_gold += barrel.quantity * barrel.price
        # update DB to take into account barrelt that were delivered
        # update gold that was recieved
        if (result[0] < total_gold):
            print("insufficient gold.")
            return "NOPE"

        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory 
            SET num_green_ml = num_green_ml + {mls_delivered}, 
            gold = gold - {total_gold}
            WHERE id = 1
        """))
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    # keep track of ml and potion count for each color
    color_ml = {
        "red": 0,
        "green": 0,
        "blue": 0
    }
    color_potions = {
        
    }
    gold = 0
    num_re = re.compile("num_(\w+)_potions")
    color = None
    # buy BARRELS of any color when we are short of said color and have sufficient money
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_red_potions, num_green_potions, num_blue_potions, gold 
            FROM global_inventory
            WHERE id = 1
        """))
        print(result.mappings().all())
        for idx, key in enumerate(result.keys()):
            if (color := num_re.match(key)):
                # add color to color_potions
                print(color)
                color_potions[color] = result.first()[idx]

        print(color_potions)
        if (not (result := result.first())):
            print('Id not found.')
            return []
        # iterate through keys and update color_potions correspondingly
        num_green = result[0]
        gold = result[1]
        if (num_green < 10):
            # find green barrel within catalog
            for barrel in wholesale_catalog:
                if barrel.sku == "SMALL_GREEN_BARREL" and \
                    barrel.quantity >= 1:
                    
                    # get price and purhcase 1 if we have enough
                    price = barrel.price
                    if (gold < price):
                        print("Insufficient gold.")
                        return []
            
                    print("purchased green barrel")
                    # update gold to reflect this
                    return [
                        {
                            "sku": "SMALL_GREEN_BARREL",
                            "quantity" : 1
                        }
                    ]
                    
    print(wholesale_catalog)

    return [
    ]

