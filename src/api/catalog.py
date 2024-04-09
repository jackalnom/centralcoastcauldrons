from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        # result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory"))
    print("here is the result", result)
    for row in result:
        print("row", row)

    # return [
    #         {
    #             "sku": "RED_POTION_0",
    #             "name": "red potion",
    #             "quantity": 1,
    #             "price": 50,
    #             "potion_type": [100, 0, 0, 0],
    #         }
    #     ]
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": row[0],
                "price": 50,
                "potion_type": [0, 100, 0, 0]
            }
        ]
