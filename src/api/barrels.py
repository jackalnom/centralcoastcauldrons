from fastapi import APIRouter, Depends
from src.api import auth
from ..models.global_inventory import GlobalInventory
from ..models.global_inventory import Barrel
from ..models.wholesale_inventory import WholesaleInventory

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)



@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print("barrels/deliver: barrels_delivered -> ", barrels_delivered)
    return GlobalInventory.get_singleton().accept_barrels_delivery(barrels_delivered)


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("barrels/plan: wholesale_catalog -> ", wholesale_catalog)

    wholesale_plan = WholesaleInventory.get_wholesale_plan(wholesale_catalog)

    return wholesale_plan
