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
    return f"R{potion.potion_type[0]}G{potion.potion_type[1]}B{potion.potion_type[2]}D{potion.potion_type[3]}"

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
                # sku alrd exists
            result_current_count = connection.execute(sqlalchemy.text(f"SELECT quantity FROM potion_inventory WHERE sku = '{sku}'"))
            for row in result_current_count:
                current_count = row[0] 
            result_potion = connection.execute(sqlalchemy.text(f"UPDATE potion_inventory SET quantity = {count + current_count} WHERE sku = '{sku}' RETURNING name"))
        
            # remove ml amount from stock
            red = order.potion_type[0]
            green = order.potion_type[1]
            blue = order.potion_type[2]
            dark = order.potion_type[3]

            stock_result = connection.execute(sqlalchemy.text(f"SELECT num_red_ml,num_green_ml,num_blue_ml,num_dark_ml \
                                                                FROM global_inventory"))
            stock_list = stock_result.first()
            new_red = stock_list[0] - count * red
            new_green = stock_list[1] - count * green
            new_blue = stock_list[2] - count * blue
            new_dark = stock_list[3] - count * dark

            stock_update = connection.execute(sqlalchemy.text(f"UPDATE global_inventory \
                                                                SET num_red_ml = {new_red}, \
                                                                    num_green_ml = {new_green}, \
                                                                    num_blue_ml = {new_blue}, \
                                                                    num_dark_ml = {new_dark}"))
            name = result_potion.first()[0]

        print(f"Sucessfully delivered {count} {name} potions. New total is {current_count + count}")

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
    response = []
    # These are all the potions we want to make currently

    with db.engine.begin() as connection:
        result_potions = connection.execute(sqlalchemy.text(
            "SELECT name, sku, type_red, type_green, type_blue, type_dark, quantity \
             FROM potion_inventory"))
    inventory = result_potions.all()
    stock_dict = []
    for potion in inventory:
        stock_dict += [{
            "color": potion[0],
            "sku": potion[1],
            "type": potion[2:6],
            "quantity": potion[5]
        }]
    stock_dict.sort(key=lambda x:x["quantity"]) # sort by least barrels
    # Determine potion needs
    target_stock = 5
    request_list = []
    total_need = [0,0,0,0]
    for potion in stock_dict:
        potion_type = potion["type"]
        current_stock = potion["quantity"]
        bottles_needed = target_stock - current_stock
        request_list += [bottles_needed]
        total_need = [x + r*bottles_needed for x,r in zip(total_need, potion_type)]
    # Determine current barrel stock
    with db.engine.begin() as connection:
        result_ml = connection.execute(sqlalchemy.text(f"SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml \
                                                         FROM global_inventory"))
    current_ml = result_ml.first()
    
    for potion, num_req in zip(stock_dict, request_list):
        if num_req == 0:
            continue
        else:
            potion_type = potion["type"]
            # Figure out how much stock it would require
            ml_rq = [ml*num_req for ml in potion_type]
            max_potion = target_stock
            # Determine limiting factor, target stock is default cap
            for i in range(len(ml_rq)):
                if ml_rq[i] != 0:
                    max_potion = min(current_ml[i] // potion_type[i], max_potion)
            # generate plan, keep ledger of what is possible with current stock
            if (max_potion > 0):
                current_ml = [c - r for c,r in zip(current_ml, ml_rq)]
                print(f"Plan produces {max_potion} {potion['color']} potions...")
                response += [
                    {
                        "potion_type": potion_type,
                        "quantity": max_potion,
                    }
                ]
            
    return response
