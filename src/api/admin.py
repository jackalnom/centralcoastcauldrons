from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy
from sqlalchemy import Insert, Update
from src.models import potions_ledger_table, inventory_ledger_table

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        # clear out attribute tables
        connection.execute(sqlalchemy.text("TRUNCATE TABLE inventory CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE customers CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE potions CASCADE"))
        # connection.execute(sqlalchemy.text("TRUNCATE TABLE inventory_ledger"))
        # connection.execute(sqlalchemy.text("TRUNCATE TABLE potion_ledger"))

   
        
        # set gold to 100 and add attributes to inventory
        connection.execute(sqlalchemy.text("INSERT INTO inventory (attribute) "+\
                           "VALUES ('gold'), ('red_ml'), ('green_ml'), ('blue_ml'), ('dark_ml')"))
        connection.execute(sqlalchemy.text("INSERT INTO inventory_ledger (attribute, change, reason) "+\
                                           "VALUES (:attribute, :change, :reason)"), {
                                               "attribute": "gold",
                                               "change": 100,
                                               "reason": "admin reset"
                                           })



    return "OK"

