import sqlalchemy
from src import database as db

from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    with db.engine.begin() as connection:

        sqlpotionamt = "SELECT num_green_potions FROM global_inventory"
        sqlmlamt = "SELECT num_green_ml FROM global_inventory"

        potionamt = connection.execute(sqlalchemy.text(sqlpotionamt)).scalar()
        mlamt = connection.execute(sqlalchemy.text(sqlmlamt)).scalar()

        if(potionamt >= 1 and mlamt >= 100): 
            return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": 1,
                "price": 100,
                "potion_type": [0, 100, 0, 0],
            }
            ]
        
    return [
            {
                "sku": "",
                "name": "",
                "quantity": 0,
                "price": 0,
                "potion_type": [0, 0, 0, 0],
            }
        ]
