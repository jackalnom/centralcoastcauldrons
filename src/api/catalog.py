from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    # Get count of Red Potions
    print("Delivering Catalog...")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            quantity_red = row[1]
    if quantity_red > 0:
        print(f"Catalog contains {quantity_red} Red Potions...")
        return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": quantity_red,
                "price": 50,
                "potion_type": [100, 0, 0, 100],
            }
        ]
    else:
        print("Inventory is Empty")
        return []
