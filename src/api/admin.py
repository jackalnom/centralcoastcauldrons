from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 100
                """
            )
        )
    # TODO: Implement database write logic here
    pass
