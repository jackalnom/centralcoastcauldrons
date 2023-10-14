from fastapi import APIRouter
from src.api.database import engine as db
import sqlalchemy

from src.api.models import Inventory

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    inventory = Inventory(db.engine)
    inventory.fetch_inventory()

    catalog = []
    if inventory.num_red_potions > 0:
        catalog.append({
            "sku": "RED_POTION_0",
            "name": "red potion",
            "quantity": inventory.num_red_potions,
            "price": 10,
            "potion_type": [100, 0, 0, 0],
        })
    if inventory.num_green_potions > 0:
        catalog.append({
            "sku": "GREEN_POTION_0",
            "name": "green potion",
            "quantity": inventory.num_green_potions,
            "price": 1,
            "potion_type": [0, 100, 0, 0],
        })
    if inventory.num_blue_potions > 0:
        catalog.append({
            "sku": "BLUE_POTION_0",
            "name": "blue potion",
            "quantity": inventory.num_blue_potions,
            "price": 1,
            "potion_type": [0, 0, 100, 0],
        })
    return catalog
