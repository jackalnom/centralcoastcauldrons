from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

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
    sql_string = "UPDATE global_inventory SET "
    # update all columsn to zero, except GOLD, which will be set to 100
    with db.engine.begin() as connection:
        # For the time being, all attributes are integers, meaning we can select all keys and set them equal to zero
        res = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory WHERE id = 2"))

        if (res):
            for key in res.keys():
                if (key not in ['id', 'gold']):
                    sql_string += key + " = 0,"
            sql_string += "gold = 100"
            sql_string += " WHERE id = 2"
            connection.execute(sqlalchemy.text(sql_string))
        else:
            return "Error occured."

    return "OK"

