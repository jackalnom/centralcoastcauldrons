from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/b2b",
    tags=["b2b"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

# Taxes? Pay 20% of profit if records aren't kept. If records are
# accurate than pay 10% of profit.
class Audit(BaseModel):
    gold: int
    liters_red: int
    liters_blue: int
    liters_green: int
    liters_dark: int
    potions: list[PotionInventory]


# Gets called every other day
@router.post("/auditor")
def post_audit(audit: Audit):
    """ """

    return "OK"

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/wholesaler/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/wholesaler/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

@router.post("/bottler/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    return "OK"


# Gets called 4 times a day
@router.post("/bottler/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 5,
            }
        ]
