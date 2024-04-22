from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy import func
from src.models import potions_table

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    num_potions = num_ml = gold = 0
    
    # query the db
    with db.engine.begin() as connection:
        res = connection.execute(sqlalchemy.text("SELECT gold, red_ml, green_ml, blue_ml, dark_ml \
                                           FROM global_inventory_temp"))
        inventory = res.first()
        res = connection.execute(func.sum(potions_table.c.quantity))

        num_potions = res.scalar_one_or_none()
        gold = inventory[0]
        num_ml = sum(inventory[1:])

        return {
            "number_of_potions": num_potions if num_potions else 0,
            "ml_in_barrels": num_ml,
            "gold": gold
        }
        

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
