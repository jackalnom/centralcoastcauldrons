from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    print("CALLED get_catalog()")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_red_potions, num_blue_potions FROM global_inventory"))
    row = result.fetchone()

    # initialize catalog
    catalog = []

    # check green inventory
    if row[0] > 0:
        catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": row[0],
                "price": 40,
                "potion_type": [0, 100, 0, 0]
            })
        
    # check red inventory
    if row[1] > 0:
        catalog.append({
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": row[0],
                "price": 40,
                "potion_type": [100, 0, 0, 0]
            })
    
    # check blue inventory
    if row[2] > 0:
        catalog.append({
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": row[0],
                "price": 40,
                "potion_type": [0, 0, 100, 0]
            })
    
    print(f"catalog: {catalog}")

    return catalog