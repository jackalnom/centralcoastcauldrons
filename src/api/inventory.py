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
                                                    SELECT num_potions
                                                    FROM potions
                                                    """))
    num_potions = 0
    for row in result:
        num_potions += row.num_potions

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold
                                                    FROM global_inventory
                                                    """))
    num_ml = 0
    row = result.fetchone()
    num_ml += row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml
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
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT *
                                                    FROM global_inventory
                                                    """))
    row = result.fetchone()
    pcap = row.potion_capacity
    mlcap = row.ml_capacity
    gold = row.gold

    do_ml = row.increase_ml_capacity
    do_potion = row.increase_potion_capacity

    if gold >= 4000:
        gold = gold // 4
    else:
        gold = 0

    pcap_level = pcap // 50
    mlcap_level = mlcap // 10000

    ml_total = row.num_red_ml + row.num_green_ml + row.num_blue_ml + row.num_dark_ml
        
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT num_potions
                                                    FROM potions
                                                    """))
    potions_total = 0
    for row in result:
        potions_total += row.num_potions

    planned_potions = planned_ml = 0

    if gold >= 1000 and ml_total > (mlcap - (0.20 * mlcap)) and do_ml and mlcap_level <= pcap_level:
        planned_ml = 1
        gold -= 1000

    if gold >= 1000 and potions_total > (pcap - (0.20 * pcap)) and do_potion:
        planned_potions = 1

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
    gold_deduction = (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity) * 1000

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    UPDATE global_inventory
                                                    SET gold = gold - :gold_deduction,
                                                    potion_capacity = potion_capacity + :potion_increase,
                                                    ml_capacity = ml_capacity + :ml_increase"""),
                                                    [{"gold_deduction": gold_deduction, "potion_increase": potion_increase, "ml_increase": ml_increase}])
    print(f"Successfully increased potion_capacity by {potion_increase} and ml_capacity by {ml_increase}.")
    return "OK"
