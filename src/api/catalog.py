from fastapi import APIRouter
import sqlalchemy
from src import database as db
from ..models.retail_inventory import RetailInventory


router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    # Can return a max of 20 items.
    inventory = RetailInventory.get_inventory()
    catalog = list(map(lambda item: item.convert_to_catalog_item(), inventory))

    return catalog