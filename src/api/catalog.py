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
        result = connection.execute(sqlalchemy.text("SELECT * FROM potions "))
        try:
            inventory = result.mappings().all()
        except Exception as e:
            print(e)
            return []

    # parse quantity 
    '''
    Custom Potions??? Need more documentation on format of potions.

    potion_re = re.compile(r"num_(\w*)_potions")
    color = None 
    # iterate through keys of db and find matches to add to SKU
    for key in result.keys():
        if match := potion_re.match(key):
            color = match.group(1)
    '''
    # iterate and add to catalog if the name of the given potion color matches the regex
    for potion in inventory:
        #TODO: allow functionality to purchase more than 1 potions
        if potion["quantity"] <= 0:
            continue
        catalog.append({
            "sku": potion["potion_sku"],
            "name": potion["potion_sku"],
            "quantity": potion["quantity"],
            "price": potion["price"],
            "potion_type": [potion["red"], potion["green"], potion["blue"], potion["dark"]],
        })
    return catalog
