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
        sqlpotionamt = """SELECT 
                        num_red_potions, num_green_potions, num_blue_potions, num_dark_potions,
                        num_purple_potions, num_teal_potions, num_slospecial_potions 
                        FROM global_inventory"""
        sqlmlamt = "SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory"

        potionamt = connection.execute(sqlalchemy.text(sqlpotionamt)).fetchone()
        mlamt = connection.execute(sqlalchemy.text(sqlmlamt)).fetchone()

        #base potions:
        red_potions, green_potions, blue_potions, dark_potions = 0, 0, 0, 0
        #special potions:
        purple_potions, teal_potions, slospecial_potions = 0, 0, 0
        red_ml, green_ml, blue_ml, dark_ml = 0, 0, 0, 0

        if potionamt is not None:
            red_potions = potionamt[0]
            green_potions = potionamt[1]
            blue_potions = potionamt[2]
            dark_potions = potionamt[3]
            purple_potions = potionamt[4]
            teal_potions = potionamt[5]
            slospecial_potions = potionamt[6]

        if mlamt is not None:
            red_ml = mlamt[0]
            green_ml = mlamt[1]
            blue_ml = mlamt[2]
            dark_ml = mlamt[3]

        #catalog list to be returned
        catalog = []

        #if we have at least one red potion, add 1 red potion to catalog
        if red_potions >= 1 and red_ml >= 100:
            catalog.append({
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": potionamt[0],
                "price": 20,
                "potion_type": [1, 0, 0, 0],
            })

        #green
        if green_potions >= 1 and green_ml >= 100:
            catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": potionamt[1],
                "price": 20,
                "potion_type": [0, 1, 0, 0],
            })

        #blue
        if blue_potions >= 1 and blue_ml >= 100:
            catalog.append({
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": potionamt[2],
                "price": 20,
                "potion_type": [0, 0, 1, 0],
            })

        #dark
        if dark_potions >= 1 and dark_ml >= 100:
            catalog.append({
                "sku": "DARK_POTION_0",
                "name": "dark potion",
                "quantity": potionamt[3],
                "price": 20,
                "potion_type": [0, 0, 0, 1],
            })

        #purple
        if purple_potions >= 1 and red_ml >= 50 and blue_ml >= 50:
            catalog.append({
                "sku": "PURPLE_POTION_0",
                "name": "purple potion",
                "quantity": potionamt[4],
                "price": 40,
                "potion_type": [0.5, 0, 0.5, 0],
            })

        #teal
        if teal_potions >= 1 and blue_ml >= 50 and green_ml >= 50:
            catalog.append({
                "sku": "TEAL_POTION_0",
                "name": "teal potion",
                "quantity": potionamt[5],
                "price": 40,
                "potion_type": [0, 0.5, 0.5, 0],
            })

        #slo special
        if slospecial_potions >= 1 and red_ml >= 25 and green_ml >= 25 and blue_ml >= 25 and dark_ml >= 25:
            catalog.append({
                "sku": "SLOSPECIAL_POTION_0",
                "name": "slo special potion",
                "quantity": potionamt[6],
                "price": 50,
                "potion_type": [0.25, 0.25, 0.25, 0.25],
            })

    return catalog