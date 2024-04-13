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
        barrels_to_purchase = []
        for barrel in wholesale_catalog:
            potion_type = [barrel.potion_type[0] * 100, barrel.potion_type[1] * 100, barrel.potion_type[2] * 100, barrel.potion_type[3] * 100]
            sql_to_execute = f"SELECT * FROM potion_catalog_items WHERE potion_type = '{potion_type_tostr(potion_type)}'"
            result = connection.execute(sqlalchemy.text(sql_to_execute))
            if result.fetchone() is None:
                continue
            potion = result.fetchone()._asdict()
            if potion["quantity"] < 10:
                barrels_to_purchase.append(barrel)

        barrels = []
        barrels_to_purchase.sort(key=lambda x: x.ml_per_barrel/barrel.price, reverse=True)
        sql_to_execute = "SELECT * FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        global_inventory = result.fetchone()._asdict()
        running_total = global_inventory["gold"]

        for barrel in barrels_to_purchase:
            if barrel.price <= running_total:
                running_total -= barrel.price
                barrels.append(
                    {
                        "sku": barrel.sku,
                        "quantity": 1,
                    }
                )
        print(f"barrels: {barrels}")
        return barrels