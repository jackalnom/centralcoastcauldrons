from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    colors_list = ["red","green","blue"]
    colors_dict = {
        "red":[100,0,0,0],
        "green":[0,100,0,0],
        "blue":[0,0,100,0]
    }
    caps_dict = {
        "red":"RED",
        "green":"GREEN",
        "blue":"BLUE"
    }
    cost_dict = {
        "red":50,
        "green":55,
        "blue":60
    }
    return_list = []
    # Get count of Red Potions
    print("Delivering Catalog...")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"SELECT sku,type_red,type_blue,type_green,cost,quantity FROM potion_inventory WHERE quantity > 0"))
    for row in result:
        sku = row[0]
        red = row[1]
        green = row[2]
        blue = row[3]
        cost = row[4]
        quantity = row[5]
        print(f"Catalog contains {quantity} {sku}...")
        return_list += [
                {
                    "sku": sku,
                    "name": f"Green Potion",
                    "quantity": quantity,
                    "price": cost,
                    "potion_type": [red,green,blue,0],
                }
            ]

        if len(return_list) >= 20:
            break

    # Depreciated, single color support
    # for color in colors_list:
    #     with db.engine.begin() as connection:
    #         result = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
    #     for row in result:
    #         quantity_potions = row[0]
    #     return_list = []
    #     if quantity_potions > 0:
    #         print(f"Catalog contains {quantity_potions} {color} potions...")
    #         return_list += [
    #             {
    #                 "sku": f"{caps_dict[color]}_POTION_0",
    #                 "name": f"{color} potion",
    #                 "quantity": quantity_potions,
    #                 "price": cost_dict[color],
    #                 "potion_type": colors_dict[],
    #             }
    #         ]
    return return_list