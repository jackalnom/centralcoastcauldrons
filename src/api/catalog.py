from fastapi import APIRouter

from src.api.audit import get_inventory

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    inventory = get_inventory()
    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": inventory["number_of_potions"],
                "price": 60,
                "potion_type": [100, 0, 0, 0],
            }
        ]
