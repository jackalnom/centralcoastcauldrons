from fastapi import APIRouter
import sqlalchemy
from src import database as db
from ..models.global_inventory import GlobalInventory


router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    catalog = GlobalInventory.get_singleton().get_catalog()

    return catalog 
