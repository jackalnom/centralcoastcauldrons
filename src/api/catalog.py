from fastapi import APIRouter
from src.api.database import engine as db
import sqlalchemy

from src.api.models import Inventory, PotionsInventory

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.


    potions = PotionsInventory(db.engine)
    potion_entries = potions.get_inventory()

    catalog = []
    for potion_entry in potion_entries:
        print(potion_entry)
        if potion_entry[2] > 0:
            catalog.append(
                {
                    "sku": potion_entry[3],
                    "potion_type": potion_entry[1],
                    "quantity": potion_entry[2],
                    "price": potion_entry[4],
                    "name": potion_entry[3]
                }
            )
    print(catalog)
    return catalog
