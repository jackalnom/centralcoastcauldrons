from fastapi import APIRouter
import sqlalchemy
from src.api import database as db
from src.api import colors as colorUtils

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    inventory = db.get_global_inventory()
    ans = []
    colors = ["red", "green", "blue"]
    for color in colors:
        num_potions = inventory[f"num_{color}_potions"]
        if num_potions >= 1:
            ans.append(
                {
                    "sku": f"{color.upper()}_POTION_0",
                    "name": "{color} potion",
                    "price": 50,
                    "potion_type": colorUtils.get_base_potion_type(color),
                    "quantity": 1,
                }
            )

    return ans
