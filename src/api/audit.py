from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src.api.database import engine as db
import sqlalchemy

from src.api.models import Inventory

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()

    return {"number_of_potions": inventory.num_blue_potions + inventory.num_green_potions + inventory.num_red_potions, "ml_in_barrels": inventory.num_blue_ml + inventory.num_green_ml + inventory.num_red_ml,"gold": inventory.gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
