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
    with db.engine.begin() as connection:
      result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
      first_row = result.first()
    return {"gold": first_row.gold, "number_of_red_potions": first_row.num_red_potions, "red_ml_in_barrels": first_row.num_red_ml, \
            "number_of_green_potions": first_row.num_green_potions, "green_ml_in_barrels": first_row.num_green_ml, \
            "number_of_blue_potions": first_row.num_blue_potions, "blue_ml_in_barrels": first_row.num_blue_ml}

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
