from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    return_list = []
    # Get count of Red Potions
    print("Delivering Catalog...")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            "SELECT \
            potion_inventory.sku \
            potion_inventory.type_red, \
            potion_inventory.type_green, \
            potion_inventory.type_blue, \
            potion_inventory.type_dark, \
            potion_inventory.cost \
            potion_inventory.name, \
            CAST(SUM(d_quan) AS INTEGER) AS total \
            FROM potion_inventory \
            join potion_ledger on potion_ledger.potion_id = potion_inventory.id \
            GROUP BY potion_inventory.id"))
    for row in result:
        sku = row[0]
        red = row[1]
        green = row[2]
        blue = row[3]
        dark = row[4]
        cost = row[5]
        name = row[6]
        quantity = row[7]
        print(f"Catalog contains {quantity} {sku}...")
        if quantity > 0:
            return_list += [
                    {
                        "sku": sku,
                        "name": f"{name}",
                        "quantity": quantity,
                        "price": cost,
                        "potion_type": [red,green,blue,dark],
                    }
                ]

        if len(return_list) >= 20:
            break
    print("Current Catalog:")
    print(return_list)
    return return_list