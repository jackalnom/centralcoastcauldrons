from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/inventory")
def get_inventory():
    """ """

    inventory = db.get_global_inventory()
    return {
        "number_of_potions": inventory["num_red_potions"],
        "ml_in_barrels": inventory["num_red_ml"],
        "gold": inventory["gold"],
    }


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
