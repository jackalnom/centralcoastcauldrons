from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        for potion in potions_delivered:
            if potion.potion_type == [0, 100, 0, 0]:
                current_potions = row["num_green_potions"]
                sql_to_execute = f"UPDATE global_inventory SET num_green_potions = {current_potions + potion.quantity}, num_green_ml = num_green_ml - {potion.quantity * 100}"
                connection.execute(sqlalchemy.text(sql_to_execute))
            elif potion.potion_type == [100, 0, 0, 0]:
                current_potions = row["num_red_potions"]
                sql_to_execute = f"UPDATE global_inventory SET num_red_potions = {current_potions + potion.quantity}, num_red_ml = num_red_ml - {potion.quantity * 100}"
                connection.execute(sqlalchemy.text(sql_to_execute))
            elif potion.potion_type == [0, 0, 100, 0]:
                current_potions = row["num_blue_potions"]
                sql_to_execute = f"UPDATE global_inventory SET num_blue_potions = {current_potions + potion.quantity}, num_blue_ml = num_blue_ml - {potion.quantity * 100}"
                connection.execute(sqlalchemy.text(sql_to_execute))
    
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        bottling_plan = []
        if row["num_green_ml"] != 0:
            bottling_plan.append(
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": row["num_green_ml"] // 100
                }
            )
        if row["num_red_ml"] != 0:
            bottling_plan.append(
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": row["num_red_ml"] // 100
                }
            )
        if row["num_blue_ml"] != 0:
            bottling_plan.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": row["num_blue_ml"] // 100
                }
            )
        return bottling_plan
