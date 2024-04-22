from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import Insert
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api import catalog
from src.helper import potion_type_name, get_potion_type
import re
from src.models import potions_table, global_table

# RED, GREEN, BLUE, DARK
POTION_THRESEHOLD = [3, 3, 2, 1]


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
    inventory = [0, 0, 0, 0]
    needs = []

    # regex for bottles
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT red_ml, green_ml, blue_ml, dark_ml
            FROM global_inventory_temp
        """))
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.

        inventory = list(result.first())


        print("inventory ", inventory)
        # we want to produce at least 1 custom potion for the meantime, we will have this be known
        # as potion thresehold
        # DEFAULT POTIONS - fully red, green, blue or dark
        potion_type = [0, 0, 0, 0]
        for idx in range(len(inventory)):
            potions_produced = inventory[idx] // 100
            potion_type[idx] = 100

            # check potion thresehold
            if (potions_produced == 0):
                continue;

            # calculating any ml leftover
            if (potions_produced > POTION_THRESEHOLD[idx]):
                print(potion_type, inventory[idx], potions_produced)
                # subtract by thresehold, this will be used to create custom potions
                inventory[idx] = inventory[idx] - ((potions_produced * 100) - (POTION_THRESEHOLD[idx] * 100))
                potions_produced = POTION_THRESEHOLD[idx] 
            else:
                inventory[idx] = inventory[idx] - (potions_produced * 100)



            needs.append(
                {
                    "potion_type": potion_type.copy(),
                    "quantity": potions_produced,
                }
            )
            potion_type[idx] = 0

        # CUSTOM POTIONS
        # use remaining mls to create some wacky potion
        # calculate most custom potions we can make
        total_ml = extra_ml = 0
        max_ml_idx = 0
        for idx in range(1, len(inventory)):
            if  inventory[max_ml_idx] < inventory[idx]:
                max_ml_idx = idx 
            total_ml += inventory[idx]
        custom_created = total_ml // 100

        if custom_created > 0:
            # remove from max element if necessary
            extra_ml = (total_ml - (custom_created * 100))
            if (extra_ml):
                inventory[max_ml_idx] -= extra_ml
            # iterate through all available ml again and calculate "amount" per color
            potion_type = [0, 0, 0, 0]
            cur_sum = 0
            for idx in range(len(inventory)):
                potion_type[idx] = inventory[idx] // custom_created
            print(total_ml, custom_created, inventory)
            if ((cur_sum := sum(potion_type))!= 100):
                potion_type[max_ml_idx] += (100 - cur_sum)
            needs.append({
                            "potion_type": potion_type,
                            "quantity": custom_created,
                        })
         
        # if more ml is needed, add from max element
        # update db to reflect the ml that the goblin took
        connection.execute(global_table.update().values({
            "red_ml": inventory[0],
            "green_ml": inventory[1],
            "red_ml": inventory[2],
            "dark_ml": inventory[3]
        }))
        # may be a mistake adding it to plan rather than when we recieve the potions.
        print(needs)
        return needs 

if __name__ == "__main__":
    print(get_bottle_plan())