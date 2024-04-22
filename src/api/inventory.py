from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        global_inventory_sql = "SELECT SUM(gold) FROM gold_ledger"
        result = connection.execute(sqlalchemy.text(global_inventory_sql))
        gold = result.fetchone()[0]
        potion_catalog_sql = "SELECT SUM(quantity) FROM potions"
        result = connection.execute(sqlalchemy.text(potion_catalog_sql))
        num_potions = result.fetchone()[0]
        barrels_sql = "SELECT SUM(potion_ml) FROM barrels"
        result = connection.execute(sqlalchemy.text(barrels_sql))
        num_ml = result.fetchone()[0]
  
        
        print(f"num_potions: {num_potions} num_ml: {num_ml} gold: {gold}")    
        return [
                {
                    "number_of_potions": num_potions,
                    "ml_in_barrels": num_ml,
                    "gold": gold,
                }
            ]

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        gold_sql = "SELECT SUM(gold) FROM gold_ledger"
        result = connection.execute(sqlalchemy.text(gold_sql))
        gold = result.fetchone()[0]
        inventory_sql = "SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(inventory_sql))
        row_inventory = result.fetchone()._asdict()
        if row_inventory["potion_capacity_plan"] + row_inventory["ml_capacity_plan"] < (gold // 1000):
            print(f"potion capacity: {row_inventory['potion_capacity_plan']} ml capacity: {row_inventory['ml_capacity_plan']} gold: {row_inventory['gold']}")
            return {
                "potion_capacity": row_inventory["potion_capacity_plan"],
                "ml_capacity": row_inventory["ml_capacity_plan"],
            }
        else:
            print("Invalid capacity plan. Not enough gold to purchase planned capacity.")
            return {
                "potion_capacity": 0,
                "ml_capacity": 0,
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
    print(f"order_id: {order_id} potion_capacity: {capacity_purchase.potion_capacity} ml_capacity: {capacity_purchase.ml_capacity}")

    with db.engine.begin() as connection:   
        capacity_update_sql = "UPDATE global_inventory SET potion_capacity_units = potion_capacity_units + :potion_capacity, ml_capacity_units = ml_capacity_units + :ml_capacity"
        connection.execute(sqlalchemy.text(capacity_update_sql), 
                           [{"potion_capacity": capacity_purchase.potion_capacity, 
                             "ml_capacity": capacity_purchase.ml_capacity}])
        gold_sql = "INSERT INTO gold_ledger (order_id, gold) VALUES (:order_id, :gold)"
        connection.execute(sqlalchemy.text(gold_sql),
                           [{"order_id": order_id, 
                          "gold": -1000 * (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity)}])


    return "OK"
