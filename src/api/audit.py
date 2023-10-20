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
      global_inventory = connection.execute(sqlalchemy.text("""
        SELECT
          SUM(change_gold) as gold, 
          SUM(change_red_ml + change_green_ml + change_blue_ml + change_dark_ml) as ml_in_barrels
        FROM global_inventory_entries
        """)).first()
      number_of_potions = connection.execute(sqlalchemy.text("""
        SELECT COALESCE(SUM(change), 0) as number_of_potions
        FROM potion_entries
        """)).first().number_of_potions
    return {"number_of_potions": number_of_potions, "ml_in_barrels": global_inventory.ml_in_barrels, "gold": global_inventory.gold}


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
