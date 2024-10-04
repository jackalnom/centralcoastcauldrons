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
    """ """
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

#subtract num_green_ml from barrels and turn it into num_green_potions
#num_green_ml goes down
#num_green_potions goes up
#for each potion delivered, add potions_delivered.quantity[0] to num_green_potions
#for each potion delivered, subtract potions_delivered.quantity[0] * 100 from num_green_ml 
    with db.engine.begin() as connection:
        numgreenml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory ")).scalar()

        if(numgreenml >= 100):
            changemltopotions = len(potions_delivered) * 100
            numpotions = len(potions_delivered) * potions_delivered.quantity[0]
            
            sqlmltopotions = f"UPDATE global_inventory SET num_green_ml = (num_green_ml - {changemltopotions})"
            sqlnumpotions = "UPDATE global_inventory SET num_green_potions = (num_green_potions + potions_delivered.quantity[0])"

            connection.execute(sqlalchemy.text(sqlmltopotions)).scalar()
            connection.execute(sqlalchemy.text(sqlnumpotions)).scalar()

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.

    with db.engine.begin() as connection:
        greenml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory ")).scalar()

    #if we have enough green ml to make 1 bottle, make 1 green bottle
    if(greenml >= 100):
        #potion type: red, green, blue, dark  
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1,
                }
            ]
    
    return[]

if __name__ == "__main__":
    print(get_bottle_plan())
