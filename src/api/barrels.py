from fastapi import APIRouter, Depends
from src.api import auth
from ..models.global_inventory import GlobalInventory
from ..models.global_inventory import Barrel

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)



@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    return GlobalInventory.get_singleton().accept_barrels_delivery(barrels_delivered)


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    wholesale_plan = GlobalInventory.get_singleton().get_wholesale_plan(wholesale_catalog)

    return wholesale_plan
