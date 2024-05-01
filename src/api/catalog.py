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
        result = connection.execute(sqlalchemy.text("""SELECT potions_catalog.sku, price, parts_red, parts_green, parts_blue, parts_dark, num_potions
                                                    FROM potions_catalog
                                                    LEFT JOIN potions_inventory ON potions_catalog.sku = potions_inventory.sku"""))

    # initialize catalog
    catalog = []

    # iterate through potions with six highest quantities in database 
    for i in range(6):
        row = result.fetchone()
        if row == None:
            break
        if row.num_potions and row.num_potions > 0:
            catalog.append({
                "sku": row.sku,
                "name": row.sku,
                "quantity": row.num_potions,
                "price": row.price,
                "potion_type": [row.parts_red, row.parts_green, row.parts_blue, row.parts_dark]
            })

    
    print(f"catalog: {catalog}")

    return catalog