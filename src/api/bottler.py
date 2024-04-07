from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from api import catalog

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
async def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    num_green_potions = 0
    delivered_green_potions = 0 
    gold_gained = 0
    # get prices for every potion
    cat = await catalog.get_catalog()
    if (not cat):
        return "NOPE"

     
    # treating only as if green potions are being delivered
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_green_potions
            FROM global_inventory
            WHERE id = 1
        """))
        # check if it is even possible to send that many
        if (not (result := result.first())):
            return "NOPE"

        num_green_potions = result[0]
        delivered_green_potions = sum(delivery.quantity for delivery in potions_delivered if delivery.potion_type == [0, 0, 100, 0])
        # really bad implementation finding total_gold gained
        for potion in cat:
            if potion.potion_type == [0, 0, 100, 0]:
                gained_gold = delivered_green_potions * potion.price
                break
        
        if delivered_green_potions == 0 or (num_green_potions < delivered_green_potions):
            return "NOPE"
        
        # update db to account for delivery of potions
        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory
            SET num_green_potions = num_green_potions - {delivered_green_potions},
            SET gold = gold + {gained_gold}
            WHERE id = 1
        """))
            
    
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    green_ml = None
    green_potions = None
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_green_potions, num_green_ml
            FROM global_inventory
            WHERE id = 1
        """))
        result = result.all()
        if (len(result) == 0 ):
            print("Inventory not found.")
            return []
        result = result[0]
        green_potions = result[0]
        green_ml = result[1]
        
        
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.

        # Initial logic: bottle all barrels into red potions.

        # bottle into green potions if we can
        green_produced = green_ml // 100

        # update db with corresponding new value
        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory
            SET num_green_ml = {green_ml - (green_produced * 100)},
                num_green_potions = {green_produced + green_potions}
            WHERE id = 1
        """))

        print(green_produced)

        return [
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": green_produced,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())