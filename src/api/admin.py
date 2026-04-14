from itertools import product

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
                gold = 100,
                red_ml = 0,
                blue_ml = 0,
                green_ml = 0,
                red_potions = 0,
                green_potions = 0,
                blue_potions= 0
                """
            )
        )

        connection.execute(sqlalchemy.text("TRUNCATE TABLE potion_inventory RESTART IDENTITY"))

        # Generate potion combinations with increments of 25 per type
        for red, green, blue, dark in product(range(0, 101, 25), repeat=4):
            if red + green + blue + dark == 100:
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO potion_inventory (red_ml, blue_ml, green_ml, dark_ml, quantity)
                        VALUES (:red, :green, :blue, :dark, 0)
                        """),
                        [{"red": red, "green" : green, "blue" : blue, "dark" : dark}])

    
