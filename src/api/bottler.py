from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
from ..models.global_inventory import GlobalInventory, PotionInventory
from ..models.retail_inventory import RetailInventory
from ..models.wholesale_inventory import WholesaleInventory
# from ..models.global_inventory import PotionInventory

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)



@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print("deliver/potions: potions delivered -> ", potions_delivered)
    return RetailInventory.accept_potions_delivery(potions_delivered)

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    bottlerPlan = WholesaleInventory.get_bottler_plan()

    return bottlerPlan
