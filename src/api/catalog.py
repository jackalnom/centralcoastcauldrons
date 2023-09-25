import sqlalchemy
from fastapi import APIRouter

from src.api.audit import get_inventory
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        sql_to_execute = sqlalchemy.text("select * from global_inventory")
        result = connection.execute(sql_to_execute).one()
    # Can return a max of 20 items.
    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": result[0],
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
