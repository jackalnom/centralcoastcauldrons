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
            sql_to_execute = f"UPDATE barrel_inventory SET potion_ml = potion_ml + {barrel.ml_per_barrel * barrel.quantity} WHERE barrel_type = '{potion_type_tostr(barrel.potion_type)}'"
            connection.execute(sqlalchemy.text(sql_to_execute))
            sql_to_execute = f"UPDATE global_inventory SET gold = gold - {barrel.price * barrel.quantity}"
            connection.execute(sqlalchemy.text(sql_to_execute))
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        max_ml_sql = "SELECT ml_capacity_units FROM global_plan"
        result = connection.execute(sqlalchemy.text(max_ml_sql))
        max_ml = result.fetchone()[0] * 10000
        ml_sql = "SELECT SUM(potion_ml) FROM barrel_inventory"
        result = connection.execute(sqlalchemy.text(ml_sql))
        ml = result.fetchone()[0]
        available_ml = max_ml - ml
        gold_sql = "SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(gold_sql))
        global_inventory = result.fetchone()._asdict()
        running_total = global_inventory["gold"]
        wholesale_catalog.sort(key=lambda x: x.ml_per_barrel/x.price, reverse=True)
        barrel_plan = []
        barrel_inventory_sql = "SELECT * FROM barrel_inventory"
        result = connection.execute(sqlalchemy.text(barrel_inventory_sql))
        rows = result.fetchall()
        barrel_inventory = [row._asdict() for row in rows]
        barrel_inventory.sort(key=lambda x: x["potion_ml"])
        for potion_type in barrel_inventory:
            if potion_type["potion_ml"] > global_inventory["ml_threshold"]:
                continue
            for barrel in wholesale_catalog:
                if barrel.ml_per_barrel > available_ml:
                    continue
                if barrel.price > running_total:
                    continue
                if potion_type["barrel_type"] == barrel.potion_type:
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