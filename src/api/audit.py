import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
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
        sql_to_execute = sqlalchemy.text("select * from global_inventory")
        result = connection.execute(sql_to_execute)
        connection.close()
        for row in result:
            print(row)
    return {"number_of_potions": result.potions_match, "ml_in_barrels": result.barrels_match, "gold": result.gold_match}

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
