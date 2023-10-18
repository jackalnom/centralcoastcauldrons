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
        sku = generate_sku(order)
        
        p_id = db.get_potion_id(sku)
        db.update_potion(count, p_id, f"Delivery of {count} {sku}")

        db.update_ml(-order.potion_type[0]*count, 'red', f"Delivery of {count} {sku}")
        db.update_ml(-order.potion_type[1]*count, 'green', f"Delivery of {count} {sku}")
        db.update_ml(-order.potion_type[2]*count, 'blue', f"Delivery of {count} {sku}")
        db.update_ml(-order.potion_type[3]*count, 'dark', f"Delivery of {count} {sku}")
        
        print(f"Sucessfully delivered {count} {sku} potions.")

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
            "SELECT \
            potion_inventory.name, \
            potion_inventory.type_red, \
            potion_inventory.type_green, \
            potion_inventory.type_blue, \
            potion_inventory.type_dark, \
            SUM(d_quan) \
            FROM potion_inventory \
            join potion_ledger on potion_ledger.potion_id = potion_inventory.id \
            GROUP BY potion_inventory.id"))
    inventory = result_potions.all()
    stock_dict = []
    for potion in inventory:
        stock_dict += [{
            "color": potion[0],
            "type": potion[2:6],
            "quantity": potion[5]
        }]
    stock_dict.sort(key=lambda x:x["quantity"]) # sort by least barrels
    # Determine potion needs
    target_stock = 15
    request_list = []
    total_need = [0,0,0,0]
    for potion in stock_dict:
        potion_type = potion["type"]
        current_stock = potion["quantity"]
        bottles_needed = target_stock - current_stock
        request_list += [bottles_needed]
        total_need = [x + r*bottles_needed for x,r in zip(total_need, potion_type)]
    # Determine current barrel stock
    
    current_ml = db.get_all_ml()
    
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
