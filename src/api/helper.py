from typing import Any
from src import database as db
import sqlalchemy
def get_global_inventory() -> sqlalchemy.Row[Any]:
    """
    Return global invetory as (gold, red_ml, green_ml, blue_ml, red_potions, green_potions, blue_potions)
    """

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT gold, red_ml, green_ml, blue_ml, red_potions, green_potions, blue_potions
                FROM global_inventory
                """
            )
        ).one()
    return row

def add_global_inventory(column: str, value: int | float) -> None:
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                f"""
                UPDATE global_inventory 
                SET {column} = {column} + :value
                """
            ),
            [{"value": value}]
        )