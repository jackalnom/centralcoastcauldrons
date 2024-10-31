from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.api import auth
import math

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    #return total number potions and ml, add the differnt color amounts together 
    #need sql

    sqltotalpotions = "SELECT inventory FROM potions_mixes ORDER BY name"
    sqltotalml = "SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory"
    sqlcurrentgold = "SELECT gold FROM global_inventory"

    with db.engine.begin() as connection:
        totalpotions = connection.exectute(sqlalchemy.text(sqltotalpotions))
        totalml = connection.exectute(sqlalchemy.text(sqltotalml))
        currentgold = connection.exectute(sqlalchemy.text(sqlcurrentgold))

    return {"number_of_potions": totalpotions, "ml_in_barrels": totalml, "gold": currentgold}

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
