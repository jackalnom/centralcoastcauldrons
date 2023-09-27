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
        get_catalog_sql = sqlalchemy.text("select * from global_inventory")
        print("get_catalog_sql: ", get_catalog_sql)
        result = connection.execute(get_catalog_sql).one()
        print("Executed get_catalog_sql, result: ", result)
    # Can return a max of 20 items.
    payload = [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": result[0],
                "price": 45,
                "potion_type": [100, 0, 0, 0],
            }
        ]
    print(payload)
    return payload
