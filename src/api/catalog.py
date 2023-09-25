from fastapi import APIRouter
from src.api.database import engine as db
import sqlalchemy

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        red_potion_no, num_red_ml, gold= result.fetchone()

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_potion_no,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
