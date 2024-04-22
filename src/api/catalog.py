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
        # result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_red_potions, num_blue_potions FROM global_inventory"))
        result = connection.execute(sqlalchemy.text("""SELECT * 
                                                    FROM potions 
                                                    WHERE num_potions > 0 
                                                    ORDER BY num_potions DESC"""))

    # initialize catalog
    catalog = []

    # iterate through potions with six highest quantities in database 
    for i in range(6):
        row = result.fetchone()
        if row == None:
            break
        catalog.append({
            "sku": row.sku,
            "name": row.sku,
            "quantity": row.num_potions,
            "price": row.price,
            "potion_type": [row.parts_red, row.parts_green, row.parts_blue, row.parts_dark]
        })
    
    print(f"catalog: {catalog}")

    return catalog