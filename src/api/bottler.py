from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.helpers import potion_type_tostr
from src.api.helpers import list_floor_division
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
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            for i in range(4):
                barrel_type = [1 if j == i else 0 for j in range(4)]
                if potion.potion_type[i] == 0:
                    continue
                barrel_update_sql = "INSERT INTO barrels (order_id, barrel_type, potion_ml) VALUES (:order_id, :barrel_type, :potion_ml)"
                connection.execute(sqlalchemy.text(barrel_update_sql),
                                    [{"order_id": order_id,"barrel_type": potion_type_tostr(barrel_type), "potion_ml": (-potion.quantity * potion.potion_type[i])}])
            potion_insert_sql = "INSERT INTO potions (order_id, potion_type, quantity) VALUES (:order_id, :potion_type, :quantity)"
            connection.execute(sqlalchemy.text(potion_insert_sql),
                                [{"order_id": order_id,"potion_type": potion_type_tostr(potion.potion_type), "quantity": potion.quantity}])
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    with db.engine.begin() as connection:
        max_potion_sql = "SELECT SUM(potion_capacity_units) FROM global_plan"
        result = connection.execute(sqlalchemy.text(max_potion_sql))
        max_potion = result.fetchone()[0] * 50
        potion_sql = "SELECT SUM(quantity) FROM potions"
        result = connection.execute(sqlalchemy.text(potion_sql))
        potions = result.fetchone()[0]
        available_potions = max_potion - potions
        
        ml_inventory = [0 for _ in range(4)]
        for i in range(4):
            barrel_type = [1 if j == i else 0 for j in range(4)]
            barrel_sql = "SELECT SUM(potion_ml) FROM barrels WHERE barrel_type = :barrel_type"
            result = connection.execute(sqlalchemy.text(barrel_sql), [{"barrel_type": potion_type_tostr(barrel_type)}])
            ml_inventory[i] = result.fetchone()[0]
        potion_catalog_sql = "SELECT * FROM potion_catalog_items"
        result = connection.execute(sqlalchemy.text(potion_catalog_sql))
        potions = result.fetchall()
        potions.sort(key=lambda x: x.price, reverse=True)
        bottling_plan = []
        for potion in potions:
            potion = potion._asdict()
            quantity = list_floor_division(ml_inventory, potion["potion_type"])
            quantity = min(quantity, available_potions)
            available_potions -= quantity
            ml_inventory = [ml_inventory[i] - quantity * potion["potion_type"][i] for i in range(4)]
            if quantity > 0:
                bottling_plan.append(
                                    {"potion_type": potion["potion_type"], 
                                        "quantity": quantity
                                    }
                            )
        print(f"bottling_plan: {bottling_plan}")
        return bottling_plan
