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
        gold_sql = "SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(gold_sql))
        global_inventory = result.fetchone()._asdict()
        running_total = global_inventory["gold"]
        wholesale_catalog.sort(key=lambda x: x.ml_per_barrel/x.price, reverse=True)
        barrel_plan = []

        for barrel in wholesale_catalog:
            barrel_bought = False
            if barrel.price > running_total:
                continue
            print(f"barrel: {barrel} running_total: {running_total}")
            potion_catalog_sql = f'SELECT * FROM potion_catalog_items'
            result = connection.execute(sqlalchemy.text(potion_catalog_sql))
            potions = result.fetchall()
            potions.sort(key=lambda x: x.price, reverse=True)
            for potion in potions:
                potion = potion._asdict()
                if potion["quantity"] < 10:
                    for i in range(4):
                        if potion["potion_type"][i] == 0:
                            continue
                        if barrel.potion_type[i] == 0:
                            continue
                        barrel_plan.append(
                            {
                                "sku": barrel.sku,
                                "quantity": 1,
                            }
                        )
                        running_total -= barrel.price
                        barrel_bought = True
                        break
                if barrel_bought:
                    break
        print(f"barrel purchase plan: {barrel_plan}, running_total: {running_total}")
        return barrel_plan