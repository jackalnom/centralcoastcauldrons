from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.helpers import potion_type_tostr
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

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            for i in range(barrel.quantity):
                barrel_insert_sql = "INSERT INTO barrels (order_id, barrel_type, potion_ml) VALUES (:order_id, :barrel_type, :potion_ml)"
                connection.execute(sqlalchemy.text(barrel_insert_sql), [{"order_id": order_id, 
                                                                         "barrel_type": potion_type_tostr(barrel.potion_type), 
                                                                         "potion_ml": barrel.ml_per_barrel}])
            gold_ledger_sql = "INSERT INTO gold_ledger (order_id, gold) VALUES (:order_id, :gold)"
            connection.execute(sqlalchemy.text(gold_ledger_sql), 
                               [{"order_id": order_id, 
                                 "gold": -barrel.price * barrel.quantity}])
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        max_ml_sql = "SELECT SUM(ml_capacity_units) FROM global_plan"
        result = connection.execute(sqlalchemy.text(max_ml_sql))
        max_ml = result.fetchone()[0] * 10000
        ml_sql = "SELECT SUM(potion_ml) FROM barrels"
        result = connection.execute(sqlalchemy.text(ml_sql))
        ml = result.fetchone()[0]
        available_ml = max_ml - ml
        gold_sql = "SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(gold_sql))
        global_inventory = result.fetchone()._asdict()
        gold_sql = "SELECT SUM(gold) FROM gold_ledger"
        running_total = connection.execute(sqlalchemy.text(gold_sql)).scalar_one()
        wholesale_catalog.sort(key=lambda x: x.ml_per_barrel/x.price, reverse=True)
        barrel_plan = []
        ml_inventory = [0 for i in range(4)]
        for i in range(4):
            barrel_type = [1 if j == i else 0 for j in range(4)]
            barrel_sum_sql = "SELECT SUM(potion_ml) FROM barrels WHERE barrel_type = :barrel_type"
            result = connection.execute(sqlalchemy.text(barrel_sum_sql),
                                        [{"barrel_type": potion_type_tostr(barrel_type)}])
            ml_inventory[i] = result.fetchone()[0]
        for i in range(4):
            barrel_ml = ml_inventory[i]
            barrel_type = [j == i for j in range(4)]
            if barrel_ml > global_inventory["ml_threshold"]:
                continue
            for barrel in wholesale_catalog:
                if barrel.ml_per_barrel > available_ml:
                    continue
                if barrel.price > running_total:
                    continue
                if barrel_type == barrel.potion_type:
                    barrel_plan.append(
                        {
                            "sku": barrel.sku,
                            "quantity": 1
                        }
                    )
                    running_total -= barrel.price
                    available_ml -= barrel.ml_per_barrel
                    break

        print(f"barrel purchase plan: {barrel_plan}, running_total: {running_total}")
        return barrel_plan