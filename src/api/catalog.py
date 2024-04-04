from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
