from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from ..models.wholesale_inventory import WholesaleInventory
import math
from ..models.global_inventory import GlobalInventory, PotionInventory

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    #TODO: implement get_inventory
    """ """
    inventory = WholesaleInventory.get_inventory()
    return inventory 

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    #TODO: implement post_audit_results
    """ """
    print(audit_explanation)

    return "OK"
