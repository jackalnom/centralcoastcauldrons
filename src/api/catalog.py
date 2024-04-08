from fastapi import APIRouter
import re
import sqlalchemy
from src import database as db
router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    # keep track of inventory
    catalog = []
    # keep track of colored potions
    freq_sku = {
        "green": 0,
        "blue": 0,
        "red": 0,
        "dark": 0
    }
    inventory = None
    # list available potions
    with db.engine.begin() as connection:
        # result = connection.execute(sqlalchemy.text(f"SELECT * FROM global_inventory WHERE id = 1"))
        # get green potion prop.
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory WHERE id = 1"))
        try:
            inventory = result.all()[0]
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
            # parse color properties
            catalog.append({
                "sku": freq_sku[color],
                "name": f"{color} potion"
                "quantity": 100,
                "price": 500,
                "potion_type": [0, 100, 0, 0]
            })
    '''

    if (inventory[0] <= 0):
        return []
    
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": inventory[0],
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]
