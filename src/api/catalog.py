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
        result = connection.execute(sqlalchemy.text("""SELECT sku, price, parts_red, parts_green, parts_blue, parts_dark
                                                    FROM potions_catalog
                                                    """))
    potion_skus = {}
    for row in result:
        potion_skus[row.sku] = (row.price, [row.parts_red, row.parts_green, row.parts_blue, row.parts_dark])
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT sku as sku, SUM(num_potions) as num_potions
                                                    FROM potions_inventory
                                                    GROUP BY sku
                                                    """))

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
                "price": potion_skus[row.sku][0],
                "potion_type": potion_skus[row.sku][1]
            })

    
    print(f"catalog: {catalog}")

    return catalog