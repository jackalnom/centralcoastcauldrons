from fastapi import APIRouter
import re
import sqlalchemy
from src import database as db
from src.helper import get_potion_type
router = APIRouter()



@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    # keep track of inventory
    catalog = []
    inventory = None
    # list available potions
    with db.engine.begin() as connection:
        # result = connection.execute(sqlalchemy.text(f"SELECT * FROM global_inventory WHERE id = 2"))
        # get green potion prop.
        result = connection.execute(sqlalchemy.text("SELECT potions.potion_sku, potions.name, potions.price, " +\
                                                    "potions.red, potions.green, potions.blue, " +\
                                                    "potions.dark, COALESCE(SUM(ledger.change), 0) AS quantity " +\
                                                    "FROM potions " +\
                                                    "LEFT JOIN potion_ledger AS ledger ON " +\
                                                    "potions.potion_sku = ledger.potion_sku " +\
                                                    "GROUP BY potions.potion_sku"))

        # iterate and add to catalog if the name of the given potion color matches the regex
        # FORMAT: sku, name, price, r, g, b, d, quantity
        for potion in result:
            #TODO: allow functionality to purchase more than 1 potions
            if potion[7] <= 0:
                continue
            catalog.append({
                "sku": potion[0],
                "name": potion[1],
                "quantity": potion[7],
                "price": potion[2],
                "potion_type": [potion[3], potion[4], potion[5], potion[6]],
            })
        return catalog
