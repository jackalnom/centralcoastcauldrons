from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src.api.database import engine as db
import sqlalchemy

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """

    with db.engine.begin() as connection:
        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()
    
    return {"number_of_potions": num_red_potions, "ml_in_barrels": num_red_ml, "gold": gold, "number_of_blue_potions": num_blue_potions, "ml_in_blue_barrels": num_blue_ml, "number_of_green_potions": num_green_potions, "ml_in_green_barrels": num_green_ml}

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
