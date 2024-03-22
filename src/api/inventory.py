from fastapi import APIRouter, Depends
from pydantic import BaseModel
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
    
    return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/audit_results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"

# Gets called once a day
@router.post("/plan_capacity_purchase")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 1,
        "barrel_capacity": 1
        }


class CapacityPurchase(BaseModel):
    potion_capacity: int
    barrel_capacity: int

# Gets called once a day
@router.post("/deliver_capacity_purchase")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
