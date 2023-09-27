import os
from enum import Enum

import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src import database as db
import dotenv

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

class Column(Enum):
    POTIONS = 0
    ML_IN_BARREL= 1
    GOLD = 2

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        sql_to_execute = sqlalchemy.text("select * from global_inventory")
        result = connection.execute(sql_to_execute).one()
        payload = {"number_of_potions": result[Column.POTIONS.value], "ml_in_barrels": result[Column.ML_IN_BARREL.value], "gold": result[Column.GOLD.value]}
    return payload


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
