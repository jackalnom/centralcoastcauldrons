from fastapi import APIRouter
from src.api.database import engine as db
import sqlalchemy

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    with db.engine.begin() as connection:
        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()
        catalog = []
        if num_red_potions > 0:
            catalog.append({
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": num_red_potions,
                "price": 10,
                "potion_type": [100, 0, 0, 0],
            })
        if num_green_potions > 0:
            catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions,
                "price": 1,
                "potion_type": [0, 100, 0, 0],
            })
        if num_blue_potions > 0:
            catalog.append({
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": num_blue_potions,
                "price": 1,
                "potion_type": [0, 0, 100, 0],
            })
        return catalog
