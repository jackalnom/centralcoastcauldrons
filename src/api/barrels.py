import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src import database as db
from src.api import auth
from src.api.audit import get_inventory

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
    print(barrels_delivered)
    for barrel in barrels_delivered:
        update_inventory_sql = sqlalchemy.text("update global_inventory set num_red_ml = {0}, gold = gold - {1}"
                                               .format(barrel.ml_per_barrel * barrel.quantity,
                                                       barrel.price * barrel.quantity)
                                               )
        print("update_inventory_sql for barrel:", barrel, ": ", update_inventory_sql)
        with db.engine.begin() as connection:
            connection.execute(update_inventory_sql)
            print("Executed update_inventory_sql for barrel:", barrel)
    return "OK"




# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    inventory = get_inventory()
    print("inventory:", inventory)
    wholesale_red_barrels = list(filter(lambda barrel: barrel.potion_type == [1, 0, 0, 0], wholesale_catalog))
    print("wholesale_red_barrels:", wholesale_red_barrels)
    highest_value_barrel = max(wholesale_red_barrels, key=lambda barrel: barrel.price/barrel.ml_per_barrel)
    print("highest_value_barrel:", highest_value_barrel)
    payload = [
        {
            "sku": highest_value_barrel.sku,
            "quantity": inventory["gold"] // highest_value_barrel.price,
        }
    ]
    print("payload:", payload)
    return payload