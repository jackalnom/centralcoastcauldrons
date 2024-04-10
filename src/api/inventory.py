from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        return [
                {
                    "number_of_potions": row["num_green_potions"] + row["num_red_potions"] + row["num_blue_potions"],
                    "ml_in_barrels": row["num_green_ml"] + row["num_red_ml"] + row["num_blue_ml"],
                    "gold": row["gold"],
                }
            ]

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    sql_to_execute = f"SELECT * FROM global_plan"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        sql_to_execute = f"SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row_inventory = result.fetchone()._asdict()
        if row_inventory["gold"] < 1000:
            return {
                "potion_capacity": 0,
                "ml_capacity": 0,
            }
        else:
            if row["potion_capacity_units"] < row["ml_capacity_units"]:
                return {
                    "potion_capacity": 1,
                    "ml_capacity": 0,
                }
            else:
                return {
                    "potion_capacity": 0,
                    "ml_capacity": 1,
                }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    current_capacity_sql = "SELECT * FROM global_plan"

    with db.engine.begin() as connection:    
        result = connection.execute(sqlalchemy.text(current_capacity_sql))
        row = result.fetchone()._asdict()
        potion_capacity = row["potion_capacity_units"]
        ml_capacity = row["ml_capacity_units"]
        update_sql_to_execute = f"UPDATE global_plan SET potion_capacity_units = {potion_capacity + capacity_purchase.potion_capacity}, ml_capacity_units = {ml_capacity + capacity_purchase.ml_capacity}"

        connection.execute(sqlalchemy.text(update_sql_to_execute))


    return "OK"
