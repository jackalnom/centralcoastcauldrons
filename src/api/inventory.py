from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT SUM(num_potions) as num
                                                    FROM potions_inventory as pi
                                                    """))
    row = result.fetchone()
    num_potions = row.num

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(li.gold) as gold, 
                                                    SUM(li.num_red_ml) as red_ml, 
                                                    SUM(li.num_green_ml) as green_ml, 
                                                    SUM(li.num_blue_ml) as blue_ml, 
                                                    SUM(li.num_dark_ml) as dark_ml
                                                    FROM ledgerized_inventory as li"""))
        
    num_ml = 0
    row = result.fetchone()
    num_ml += row.red_ml + row.green_ml + row.blue_ml + row.dark_ml
    gold = row.gold
    
    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(li.gold) as gold, 
                                                    SUM(li.num_red_ml) as red_ml, 
                                                    SUM(li.num_green_ml) as green_ml, 
                                                    SUM(li.num_blue_ml) as blue_ml, 
                                                    SUM(li.num_dark_ml) as dark_ml
                                                    FROM ledgerized_inventory as li"""))
    row = result.fetchone()
    gold = row.gold
    ml_total = row.red_ml + row.green_ml + row.blue_ml + row.dark_ml
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT potion_capacity, ml_capacity, increase_ml_cap, increase_potion_cap
                                                    FROM shop_states"""))
    row = result.fetchone()

    pcap = row.potion_capacity
    mlcap = row.ml_capacity
    do_ml = row.increase_ml_cap
    do_potion = row.increase_potion_cap

    if gold >= 4000:
        gold = gold // 4
    else:
        gold = 0

    pcap_level = pcap // 50
    mlcap_level = mlcap // 10000
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT SUM(num_potions) as num_potions
                                                    FROM potions_inventory as pi
                                                    """))
    row = result.fetchone()
    potions_total = row.num_potions
    print(f"potions_total: {potions_total}")

    planned_potions = planned_ml = 0

    if gold >= 1000 and potions_total > (pcap - (0.20 * pcap)) and do_potion:
        planned_potions = 1

    if gold >= 1000 and ml_total > (mlcap - (0.20 * mlcap)) and do_ml and mlcap_level <= pcap_level:
        planned_ml = 1
        gold -= 1000

    print("mlcap diff: ", mlcap-(0.20*mlcap), " pcap diff: ", pcap-(0.20*pcap))

    return {
        "potion_capacity": planned_potions,
        "ml_capacity": planned_ml
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    potion_increase = capacity_purchase.potion_capacity * 50
    ml_increase = capacity_purchase.ml_capacity * 10000
    gold_deduction = 0
    gold_deduction -= (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity) * 1000

    if gold_deduction == 0:
        return "OK"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    UPDATE shop_states
                                                    SET potion_capacity = potion_capacity + :potion_increase,
                                                    ml_capacity = ml_capacity + :ml_increase"""),
                                                    [{"potion_increase": potion_increase, "ml_increase": ml_increase}])
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""INSERT INTO ledgerized_inventory (
                                                        order_id,
                                                        order_type,
                                                        gold,
                                                        num_red_ml,
                                                        num_green_ml,
                                                        num_blue_ml,
                                                        num_dark_ml
                                                    )
                                                    VALUES (:order_id,
                                                            :order_type, 
                                                            :gold,
                                                            0,
                                                            0,
                                                            0,
                                                            0)
                                                    """),
                                                    [{"order_id": order_id,
                                                      "order_type": "capacity",
                                                      "gold": gold_deduction}])
    print(f"Successfully increased potion_capacity by {potion_increase} and ml_capacity by {ml_increase}.")
    return "OK"
