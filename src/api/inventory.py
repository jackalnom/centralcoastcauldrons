from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT num_potions
                                                    FROM potions
                                                    """))
    num_potions = 0
    for row in result:
        num_potions += row.num_potions

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold
                                                    FROM global_inventory
                                                    """))
    num_ml = 0
    row = result.fetchone()
    num_ml += row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml
    gold = row.gold
    
    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"
