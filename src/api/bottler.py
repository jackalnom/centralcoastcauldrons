from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import Insert
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api import catalog
from src.helper import potion_type_name
import re
from src.models import potions_table

POTION_THRESEHOLD = {
    "red": 3,
    "green": 2,
    "blue": 1,
    "dark": 1
}

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
    # parsing all delivered potion to be accepted by param binding
    param_upsert = []
    # keep track of all potion_types delivered and parse as JSON
    if (len(potions_delivered) == 0):
        return "OK"
    with db.engine.begin() as connection:
        
        # if potion is already in db, simply update value, else insert
        for delivery in potions_delivered:
            name = potion_type_name(delivery.potion_type)
            param_upsert.append({
                "potion_sku": name,
                "red": delivery.potion_type[0], 
                "green": delivery.potion_type[1],
                "blue": delivery.potion_type[2],
                "dark": delivery.potion_type[3],
                "quantity": delivery.quantity
                })

        # upsertion
        stmt = Insert(potions_table).values(param_upsert)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["potion_sku"],
            set_=dict({
                "potion_sku": stmt.excluded.potion_sku,
                "red": stmt.excluded.red,
                "green": stmt.excluded.green,
                "blue": stmt.excluded.blue,
                "dark": stmt.excluded.dark,
                "quantity": potions_table.c.quantity + stmt.excluded.quantity
            })
        )

        # update db
        connection.execute(upsert_stmt)



    print(f"bottles delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from bottle to bottle.
    """
    # keep track of our needs
    inventory = {
        "red": 0,
        "green": 0,
        "blue": 0,
        "dark": 0
    }
    needs = []

    # regex for bottles
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT red_ml AS red, green_ml AS green, blue_ml AS blue, dark_ml AS dark
            FROM global_inventory_temp
        """))
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.

        barrels = result.mappings().first()
        inventory = dict(barrels)


        # we want to produce at least 1 custom potion for the meantime, we will have this be known
        # as potion thresehold
        # DEFAULT POTIONS - fully red, green, blue or dark
        params = {
            "red": 0,
            "green": 0,
            "blue": 0,
            "dark": 0
        }
        for color, value in inventory.items():
            potions_produced = value // 100
            params[color] = 100

            # check potion thresehold
            if (potions_produced == 0):
                continue;

            # calculating any ml leftover
            if (potions_produced > POTION_THRESEHOLD[color]):
                print(color, value, potions_produced)
                # subtract by thresehold, this will be used to create custom potions
                inventory[color] = value - ((potions_produced * 100) - (POTION_THRESEHOLD[color] * 100))
                potions_produced = POTION_THRESEHOLD[color] 
            else:
                inventory[color] = value - (potions_produced * 100)

            # update db to reflect the ml that the goblin took
            # may be a mistake adding it to plan rather than when we recieve the potions.
            connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory_temp
            SET {color}_ml = {color}_ml - :produced
            """), {
                "color": color,
                "produced": (potions_produced * 100)
            })

            params[color] = 0
            needs.append(
                {
                    "potion_type": color + " potion",
                    "quantity": potions_produced,
                }
            )
        return needs 

if __name__ == "__main__":
    print(get_bottle_plan())