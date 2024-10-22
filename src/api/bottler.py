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
        numredml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory ")).scalar()
        numgreenml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory ")).scalar()
        numblueml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory ")).scalar()
        # test change

#iterate through the potions deleiverd list, for every potion the if logic happens
# for every potion, have the if statements checking qhich color, then updating the according ml adn potion count
#
        if(numredml >= 100):
            changeredmltopotions = len(potions_delivered) * 100
            rednumpotions = len(potions_delivered) * potions_delivered.quantity[0]
            
            sqlredmltopotions = f"UPDATE global_inventory SET num_red_ml = (num_red_ml - {changeredmltopotions})"
            sqlrednumpotions = "UPDATE global_inventory SET num_red_potions = (num_red_potions + potions_delivered.quantity[0])"
            # this instead? -> sqlrednumpotions = f"UPDATE global_inventory SET num_red_potions = (num_red_potions + {rednumpotions})"

            connection.execute(sqlalchemy.text(sqlredmltopotions)).scalar()
            connection.execute(sqlalchemy.text(sqlrednumpotions)).scalar()

        elif(numgreenml >= 100):
            changegreenmltopotions = len(potions_delivered) * 100
            greennumpotions = len(potions_delivered) * potions_delivered.quantity[0]
            
            sqlgreenmltopotions = f"UPDATE global_inventory SET num_green_ml = (num_green_ml - {changegreenmltopotions})"
            sqlgreennumpotions = "UPDATE global_inventory SET num_green_potions = (num_green_potions + potions_delivered.quantity[0])"

            connection.execute(sqlalchemy.text(sqlgreenmltopotions)).scalar()
            connection.execute(sqlalchemy.text(sqlgreennumpotions)).scalar()

        elif(numblueml >= 100):
            changebluemltopotions = len(potions_delivered) * 100
            bluenumpotions = len(potions_delivered) * potions_delivered.quantity[0]
            
            sqlbluemltopotions = f"UPDATE global_inventory SET num_blue_ml = (num_blue_ml - {changebluemltopotions})"
            sqlbluenumpotions = "UPDATE global_inventory SET num_blue_potions = (num_blue_potions + potions_delivered.quantity[0])"

            connection.execute(sqlalchemy.text(sqlbluemltopotions)).scalar()
            connection.execute(sqlalchemy.text(sqlbluenumpotions)).scalar()

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
        #combine these selects
        redml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory ")).scalar()
        greenml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory ")).scalar()
        blueml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory ")).scalar()

    #if we have enough green ml to make 1 bottle, make 1 green bottle
    if(redml >= 100):
        #potion type: red, green, blue, dark  
        return [
                {
                    "potion_type": [1, 0, 0, 0],
                    "quantity": 1,
                }
            ]
    
    elif(greenml >= 100):
        return [
                {
                    "potion_type": [0, 1, 0, 0],
                    "quantity": 1,
                }
            ]
    if(blueml >= 100):
        return [
                {
                    "potion_type": [0, 0, 1, 0],
                    "quantity": 1,
                }
            ]
    
    else:
        return "Not enough ml to make a single bottle! :()"

if __name__ == "__main__":
    print(get_bottle_plan())
