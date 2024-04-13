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
    # keep track of colored potions
    freq_sku = {
        "green": 0,
        "blue": 0,
        "red": 0,
        "dark": 0
    }
    inventory = None
    num_potion_re = re.compile("num_(\w+)_potions")
    # list available potions
    with db.engine.begin() as connection:
        # result = connection.execute(sqlalchemy.text(f"SELECT * FROM global_inventory WHERE id = 2"))
        # get green potion prop.
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory WHERE id = 2"))
        try:
            inventory = result.mappings().first()
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
    for key, value in inventory.items():
        if (potion_key:=num_potion_re.match(key)):
            if (value <= 0):
                continue
            # select capture group that contains color
            color = potion_key.group(1)
            # check frequency and set that as the potion number

            # really poor logic
            # TODO: find way to represent potions better other than SKU???
            potion_type = None 
            potion_type = get_potion_type(color)
           
            catalog.append({
                "sku": freq_sku[color],
                "name": f"{color} potion",
                "quantity": value,
                "price": 50,
                "potion_type": potion_type,
            })
    return catalog
