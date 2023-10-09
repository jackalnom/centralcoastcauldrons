from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

def generate_sku(potion: PotionInventory):
    return f"RED_{potion.potion_type[0]}_GREEN_{potion.potion_type[1]}_BLUE_{potion.potion_type[2]}_DARK_{potion.potion_type[3]}"

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print("Delivering Potions:")
    for order in potions_delivered:
        count = order.quantity
        current_count = 0
        sku = generate_sku(order)
        with db.engine.begin() as connection:
            # check if sku exists in table already
            sku_exist_result= connection.execute(sqlalchemy.text(f"SELECT COUNT(sku) FROM potion_inventory WHERE sku = '{sku}'"))
            for row in sku_exist_result:
                sku_exist = row[0]
            if not sku_exist:
                # sku_exist = 1 if already in system
                # sku_exist = 0 if not in system
                # in this case, sku doesn't exist yet
                # insert row
                result = connection.execute(sqlalchemy.text(
                    f"INSERT INTO potion_inventory(sku, type_red, type_green, type_blue, type_dark, cost, quantity)\
                     VALUES ('{sku}', {order.potion_type[0]},{order.potion_type[1]},{order.potion_type[2]},{order.potion_type[3]},{50}, {count})"))
                print(f"Creating new entry for SKU:{sku}...")
            else:
                # sku alrd exists
                result_current_count = connection.execute(sqlalchemy.text(f"SELECT quantity FROM potion_inventory WHERE sku = '{sku}'"))
                for row in result_current_count:
                    current_count = row[0] 
                result = connection.execute(sqlalchemy.text(f"UPDATE potion_inventory SET quantity = {count + current_count} WHERE sku = '{sku}'"))
            
            # remove ml amount from stock
            red = order.potion_type[0]
            green = order.potion_type[1]
            blue = order.potion_type[2]
            dark = order.potion_type[3]

            stock_result = connection.execute(sqlalchemy.text(f"SELECT num_red_ml,num_green_ml,num_blue_ml,num_dark_ml \
                                                                FROM global_inventory"))
            stock_list = stock_result.first()
            new_red = stock_list[0]*count- red
            new_green = stock_list[1]*count - green
            new_blue = stock_list[2]*count - blue
            new_dark = stock_list[3]*count - dark

            stock_update = connection.execute(sqlalchemy.text(f"UPDATE global_inventory \
                                                                SET num_red_ml = {new_red}, \
                                                                    num_green_ml = {new_green}, \
                                                                    num_blue_ml = {new_blue}, \
                                                                    num_dark_ml = {new_dark}"))

        print(f"Sucessfully delivered {count} of SKU:{sku}. New total is {current_count + count}")

        # Depreciated, only supports monolithic potions
        # # pull and update potion delivery
        # color = delivery_dict[order.potion_type.index(100)] # still assuming pure potions
        # with db.engine.begin() as connection:
        #     result_ml = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
        #     result_potion = connection.execute(sqlalchemy.text(f"SELECT num_{color}_potions FROM global_inventory"))
        # for row in result_potion:
        #     current_potion = row[0]
        # for row in result_ml:
        #     current_ml = row[0]
        # updated_potion = current_potion + count
        # updated_ml = current_ml - count*100
        # print(f"{count} {color} potions delivered, new {color} mL stock is {updated_ml}, new {color} potion stock is {updated_potion}")
        # with db.engine.begin() as connection:
        #     result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_potions = {updated_ml}"))
        #     result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_ml = {updated_ml}"))
    print(potions_delivered)

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    response = []
    colors_list = ["red", "green", "blue", "dark"]
    potion_type_dict = {
        "red":[100,0,0,0],
        "green":[0,100,0,0],
        "blue":[0,0,100,0],
        "dark":[0,0,0,100]
    }
    # Initial logic: bottle all barrels into pure potions
    for color in colors_list:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
        for row in result:
            current_ml = row[0]
        max_bottles = current_ml // 100
        print(f"Plan produces {max_bottles} {color} potions...")
        if (max_bottles > 0):
            response += [
                    {
                        "potion_type": potion_type_dict[color],
                        "quantity": max_bottles,
                    }
                ]
    return response
