from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api import catalog
from src.helper import get_potion_type, get_color
import re

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
    # keep track of all potion_types delivered and parse as JSON
    delivered_query = ""
    if (len(potions_delivered) == 0):
        return "WOW"
    with db.engine.begin() as connection:
        # iterate and add all bottles that have been delivered to db
        for idx in range(len(potions_delivered)):
            bottle = potions_delivered[idx]
            if bottle.quantity <= 0:
                continue
            # get potion_type
            color = get_color(bottle.potion_type)

            # parse and add to delivered JSON
            delivered_query += f"num_{color}_potions = num_{color}_potions + {bottle.quantity}{',' if idx < len(potions_delivered) - 1 else ''}" 
            print("Recieved: ", color, " AMOUNT: ", bottle.quantity)

        # update bottles amount in db
        if (len(delivered_query) > 0):
            connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory
            SET {delivered_query}
            WHERE id = 1
            """))

    print(f"bottles delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from bottle to bottle.
    """
    # keep track of our needs
    color_ml = 0
    needs = []

    # regex for bottles
    num_bottle_re = re.compile("num_(\w+)_ml")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT * 
            FROM global_inventory
            WHERE id = 1
        """))
        ml_inventory = result.mappings().first()
        
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.

        # Initial logic: bottle all bottles into red potions.

        # bottle into only the three colors that we know as of recently, red, green and blue
        for key, value in ml_inventory.items():
            if (match_ml := num_bottle_re.match(key)):
                potions_produced = value // 100

                ml_name = match_ml.group(0)
                color = match_ml.group(1)
                print(color, value, potions_produced)

                if potions_produced > 0:

                    print(potions_produced)

                    # update db to reflect the ml that the goblin took
                    # may be a mistake adding it to plan rather than when we recieve the potions.
                    connection.execute(sqlalchemy.text(f"""
                    UPDATE global_inventory
                    SET {ml_name} = {ml_name} - {potions_produced * 100}
                    WHERE id = 1
                    """))

                    # get potion_type and add to the list of what we need bottled
                    potion_type = get_potion_type(color)
                    needs.append(
                        {
                            "potion_type": potion_type,
                            "quantity": potions_produced,
                        }
                    )
        return needs 

if __name__ == "__main__":
    print(get_bottle_plan())