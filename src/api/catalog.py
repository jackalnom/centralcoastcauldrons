from fastapi import APIRouter
import sqlalchemy
from src import database as db
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = """
        SELECT num_green_potions FROM global_inventory
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        num_green_potions = result.scalar() if result else 0

    green_potion_price = 50  

    catalog_item = {
        "sku": "GREEN_POTION_0",
        "name": "green potion",
        "quantity": num_green_potions,
        "price": green_potion_price,
        "potion_type": [0, 100, 0, 0], 
    }

    return [catalog_item]
