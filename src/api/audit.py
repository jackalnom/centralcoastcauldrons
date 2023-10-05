from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    print("Audit in Progress...")
    potion_count = 0
    current_ml = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory"))
        for row in result:
            potion_count += row[0]
        result = connection.execute(sqlalchemy.text("SELECT gold, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory"))
        for row in result:
            current_gold = row[0]
            current_ml += row[1]
            current_ml += row[2]
            current_ml += row[3]
            current_ml += row[4]

    print(f"Current Stats: Potions-{potion_count}, Stock in mL-{current_ml}, Gold-{current_gold}")
    return {"number_of_potions": potion_count, "ml_in_barrels": current_ml, "gold": current_gold}

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
