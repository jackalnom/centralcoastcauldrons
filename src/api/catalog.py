from fastapi import APIRouter
import sqlalchemy
from src.api import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    response = {
        "sku": "RED_POTION_0",
        "name": "red potion",
        "price": 50,
        "potion_type": 50,
        "quantity": 1,
    }
    return response
