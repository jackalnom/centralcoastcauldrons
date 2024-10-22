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
        sqlpotionamt = "SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"
        sqlmlamt = "SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"

        potionamt = connection.execute(sqlalchemy.text(sqlpotionamt)).fetchone()
        mlamt = connection.execute(sqlalchemy.text(sqlmlamt)).fetchone()

        red_potions, green_potions, blue_potions = 0, 0, 0
        red_ml, green_ml, blue_ml = 0, 0, 0

        if potionamt is not None:
            red_potions = potionamt[0]
            green_potions = potionamt[1]
            blue_potions = potionamt[2]

        if mlamt is not None:
            red_ml = mlamt[0]
            green_ml = mlamt[1]
            blue_ml = mlamt[2]

        #catalog list to be returned
        catalog = []

        #if we have at least one red potion, add 1 red potion to catalog
        if red_potions >= 1 and red_ml >= 100:
            catalog.append({
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 40,
                "potion_type": [1, 0, 0, 0],
            })

        #if we have at least one green potion, add 1 green potion to catalog
        if green_potions >= 1 and green_ml >= 100:
            catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": 1,
                "price": 40,
                "potion_type": [0, 1, 0, 0],
            })

        #if we have at least one blue potion, add 1 blue potion to catalog
        if blue_potions >= 1 and blue_ml >= 100:
            catalog.append({
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": 1,
                "price": 40,
                "potion_type": [0, 0, 1, 0],
            })

    return catalog