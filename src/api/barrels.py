import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.api.audit import get_inventory
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
    print(barrels_delivered)
    for barrel in barrels_delivered:
        sql_to_execute = sqlalchemy.text("update global_inventory set num_red_ml = {0}, gold = gold - {1}"
                                         .format(barrel.ml_per_barrel * barrel.quantity, barrel.price * barrel.quantity)
                                         )
        with db.engine.begin() as connection:
            connection.execute(sql_to_execute)
    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    inventory = get_inventory()
    to_buy = 0
    if inventory["number_of_potions"] < 10:
        to_buy = 1
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": to_buy,
        }
    ]
