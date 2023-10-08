from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    # add entries as more barrels are desired
    delivery_dict = {
        0: "red",
        1: "green",
        2: "blue",
        3: "dark"
    }
    SKIP_COLOR_KEY = "SKIP"
    for indiv_barrel in barrels_delivered:
        ml_total_delivered=0
        cost_total=0
        current_gold=0
        current_ml=0
        color = delivery_dict.get(indiv_barrel.potion_type.index(1), SKIP_COLOR_KEY)
        if(color != "SKIP"):
            ml_total_delivered = indiv_barrel.quantity*indiv_barrel.ml_per_barrel
            cost_total = indiv_barrel.quantity*indiv_barrel.price
            with db.engine.begin() as connection:
                result_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
                result_ml = connection.execute(sqlalchemy.text(f"SELECT num_{color}_ml FROM global_inventory"))
            for row in result_gold:
                current_gold = row[0] - cost_total
            for row in result_ml:
                current_ml = row[0] + ml_total_delivered
            
            print(f"Delivery taken of {ml_total_delivered}mL of {color} potion, at cost of {cost_total}.")
            print(f"Current {color} potion stock is {current_ml}mL, current gold is {current_gold}")
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_ml = {current_ml}"))
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {current_gold}"))

    ## end new implimentation 
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
   
    # Start new implimentation
    purchase_plan = []
    # add entries as more barrels are desired
    purchasing_dict = {
        # "SMALL_RED_BARREL": "red",
        "SMALL_GREEN_BARREL": "green",
        # "SMALL_BLUE_BARREL": "blue",
        # "SMALL_DARK_BARREL": "dark"
    }
    SKIP_COLOR_KEY = "SKIP"
    for for_sale in wholesale_catalog:  # go through catalog
        print("Going through catalog...")
        color = purchasing_dict.get(for_sale.sku, SKIP_COLOR_KEY)
        if color == SKIP_COLOR_KEY:
            # skip if not small barrel
            print(f"Not interested in {for_sale.sku}")
        else:
            print(f"Checking {for_sale.sku}...")

            # check current inventory
            with db.engine.begin() as connection:
                result_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))        
            for row in result_gold:
                current_gold = row[0]
            
            # buy 1/4 of possible barrels
            max_barrel = min((current_gold // for_sale.price) // len(purchasing_dict), for_sale.quantity)
            
            if max_barrel != 0:
                print(f"Purchacing {max_barrel} small {color} barrels...")
                purchase_plan += [
                    {
                        "sku": f"{for_sale.sku}",
                        "quantity": max_barrel,
                    }
                ]
    return purchase_plan