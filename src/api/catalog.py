from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        results = []
        if (row["num_green_potions"]) > 0:
            results.append(
                {
                    "sku": "GREEN_POTION",
                    "name": "Small Green Potion",
                    "quantity": row["num_green_potions"],
                    "price": 45,
                    "potion_type": [0, 100, 0, 0],
                }
            )
        elif (row["num_red_potions"]) > 0:
            results.append(
                {
                    "sku": "RED_POTION",
                    "name": "Small Red Potion",
                    "quantity": row["num_red_potions"],
                    "price": 45,
                    "potion_type": [100, 0, 0, 0],
                }
            )
        elif (row["num_blue_potions"]) > 0:
            results.append(
                {
                    "sku": "BLUE_POTION",
                    "name": "Small Blue Potion",
                    "quantity": row["num_blue_potions"],
                    "price": 45,
                    "potion_type": [0, 0, 100, 0],
                }
            )
        return results
