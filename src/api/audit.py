from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api import database as db
from src.api import colors

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/inventory")
def get_inventory():
    """ """

    inventory = db.get_global_inventory()
    number_of_potions = 0
    ml_in_barrels = 0
    for color in colors.colors:
        number_of_potions += inventory[f"num_{color}_potions"]
        ml_in_barrels += inventory[f"num_{color}_ml"]

    return {
        "number_of_potions": number_of_potions,
        "ml_in_barrels": ml_in_barrels,
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
