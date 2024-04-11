from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.helpers import potion_type_tostr
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
            sql_to_execute = f"UPDATE barrel_inventory SET potion_ml = potion_ml - {potion.quantity * 100} WHERE potion_type = '{potion_type_tostr(potion.potion_type)}'"
            connection.execute(sqlalchemy.text(sql_to_execute))
            sql_to_execute = f"UPDATE potion_catalog_items SET quantity = quantity + {potion.quantity} WHERE potion_type = '{potion_type_tostr(potion.potion_type)}'"
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

    sql_to_execute = "SELECT * FROM barrel_inventory WHERE potion_ml > 0"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        rows = result.fetchall()
        bottling_plan = []
        for row in rows:
            row = row._asdict()
            bottling_plan.append(
                {
                    "potion_type": row["potion_type"],
                    "quantity": row["potion_ml"] // 100,
                }
            )
        return bottling_plan
