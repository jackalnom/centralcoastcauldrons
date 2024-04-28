from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import Insert
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api import catalog
from src.helper import potion_type_name,  idx_to_color
import re
from src.models import potions_table, inventory_ledger_table, potions_ledger_table

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
    potion_changes = []
    barrel_changes = []
    # keep track of all potion_types delivered and parse as JSON
    if (len(potions_delivered) == 0):
        return "OK"
    with db.engine.begin() as connection:
        
        # if potion is already in db, simply update value, else insert
        for delivery in potions_delivered:
            name = potion_type_name(delivery.potion_type)
            sku = name.lower().replace(" ", '_')
            param_upsert.append({
                "potion_sku": sku,
                "name": name,
                "red": delivery.potion_type[0], 
                "green": delivery.potion_type[1],
                "blue": delivery.potion_type[2],
                "dark": delivery.potion_type[3],
                "quantity": delivery.quantity
                })
            potion_changes.append({
                "potion_sku": sku,
                "change": delivery.quantity
            })

            # iterate through red, green, blue and dark in order to get 
            for idx in range(len(delivery.potion_type)):
                if delivery.potion_type[idx] != 0:
                    barrel_changes.append({
                        "attribute": idx_to_color(idx) + "_ml",
                        "change": -1 * delivery.potion_type[idx] * delivery.quantity
                    })


        # upsertion
        stmt = Insert(potions_table).values(param_upsert).on_conflict_do_nothing()
        # upsert_stmt = stmt.on_conflict_do_update(
        #     index_elements=["potion_sku"],
        #     set_=dict({
        #         "potion_sku": stmt.excluded.potion_sku,
        #         "red": stmt.excluded.red,
        #         "green": stmt.excluded.green,
        #         "blue": stmt.excluded.blue,
        #         "dark": stmt.excluded.dark,
        #         "quantity": potions_table.c.quantity + stmt.excluded.quantity
        #     })
        # )

        # update db
        # insert into db if potion_sku doesn't exist
        connection.execute(stmt)

        # insert into potion ledger the new changes
        stmt = Insert(potions_ledger_table).values(potion_changes)
        connection.execute(stmt)

        # insert into inventoryledger the new changes
        stmt = Insert(inventory_ledger_table).values(barrel_changes)
        connection.execute(stmt)





    print(f"bottles delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from bottle to bottle.
    """
    # keep track of our needs
    inventory = [0, 0, 0, 0]
    change_inventory = [0, 0, 0, 0]
    needs = []

    # regex for bottles
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT attribute, SUM(change) as total
            FROM inventory_ledger
            GROUP BY attribute
        """))
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.
        for row in result:
            # optimizes once ml for a given color has been checked
            if not inventory[0] and row.attribute == 'red_ml':
                inventory[0] = row.total
            elif not inventory[1] and row.attribute == 'green_ml':
                inventory[1] = row.total
            elif not inventory[2] and row.attribute == 'blue_ml':
                inventory[2] = row.total
            elif not inventory[3] and row.attribute == 'dark_ml':
                inventory[3] = row.total


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
                inventory[idx] = inventory[idx] - (POTION_THRESEHOLD[idx] * 100)
                potions_produced = POTION_THRESEHOLD[idx] 
                change_inventory[idx] = POTION_THRESEHOLD[idx] * 100
            else:
                inventory[idx] = inventory[idx] - (potions_produced * 100)
                change_inventory[idx] = potions_produced * 100



            needs.append(
                {
                    "potion_type": potion_type.copy(),
                    "quantity": potions_produced,
                }
            )
            potion_type[idx] = 0

        print(inventory)
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

        print("custom created", custom_created)
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
                change_inventory[idx] += potion_type[idx] * custom_created
            print(total_ml, custom_created, inventory)
            if ((cur_sum := sum(potion_type))!= 100):
                potion_type[max_ml_idx] += (100 - cur_sum)
                change_inventory[max_ml_idx] += ((100 - cur_sum) * custom_created) 
            needs.append({
                            "potion_type": potion_type,
                            "quantity": custom_created,
                        })
         
        print(inventory)
        # if more ml is needed, add from max element
        # update db to reflect the ml that the goblin took
        # connection.execute(global_table.update().values({
        #     "red_ml": inventory[0],
        #     "green_ml": inventory[1],
        #     "blue_ml": inventory[2],
        #     "dark_ml": inventory[3]
        # }))
     
        print(inventory, change_inventory)
        print(needs)
        return needs 

if __name__ == "__main__":
    print(get_bottle_plan())