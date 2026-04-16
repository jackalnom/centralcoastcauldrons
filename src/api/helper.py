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
                SELECT gold, red_ml, green_ml, blue_ml, dark_ml
                FROM global_inventory
                """
            )
        ).one()
    return row

def add_global_inventory(column: str, value: int | float) -> None:
    """
    Add value to global inventory column
    """
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

def get_potion_inventory():
    """
    Return potions currently in invetory as (red_ml, green_ml, blue_ml, dark_ml, quantity) 
    """

    with db.engine.begin() as connection:
        rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT red_ml, green_ml, blue_ml, dark_ml, quantity
                FROM potion_inventory
                WHERE quantity > 0;
                """
            )
        ).all()
    return rows

def get_potion(id: int):
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM potion_inventory
                WHERE id = :id;
                """
            ), {"id" : id}
        ).one()
    return row

def add_potion(id: int, value: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                f"""
                UPDATE global_inventory 
                WHERE id == id :id
                SET quantity = quantity + :value
                """
            ),
            [{"value": value, "id": id}]
        )

def get_potion_count() -> int:
    """
    Get total quantity of potions in inventory.
    """
    with db.engine.begin() as connection:
        quantities = connection.execute(
            sqlalchemy.text(
                """
                SELECT quantity
                FROM potion_inventory
                """
            )
        ).all()
    
    return  sum([i.quantity for i in quantities])

def increase_potions(id: int, count: int) -> None:
    """
    Increases count of the potion with specific id.
    """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE potion_inventory 
                SET quantity = quantity + :count
                WHERE id = :id
                """
            ), {"id" : id, "count":  count}
        )