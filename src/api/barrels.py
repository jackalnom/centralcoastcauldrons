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
    gold_remaining = inventory["gold"]
    list_to_buy = []
    highest_value_barrel = min(wholesale_red_barrels, key=lambda barrel: barrel.price/barrel.ml_per_barrel)
    print("highest_value_barrel:", highest_value_barrel)

    while gold_remaining >= highest_value_barrel.price:
        quantity_to_buy = gold_remaining // highest_value_barrel.price
        list_to_buy.append({"sku": highest_value_barrel.sku, "quantity": quantity_to_buy})
        print("new state of list:", list_to_buy)
        gold_remaining -= highest_value_barrel.price * quantity_to_buy
        wholesale_red_barrels[wholesale_red_barrels.index(highest_value_barrel)].quantity -= quantity_to_buy
        if wholesale_red_barrels[wholesale_red_barrels.index(highest_value_barrel)].quantity == 0:
            wholesale_red_barrels.remove(highest_value_barrel)
        highest_value_barrel = min(wholesale_red_barrels, key=lambda barrel: barrel.price/barrel.ml_per_barrel)

    print("remaining red barrels:", wholesale_red_barrels)
    print("remaining gold:", gold_remaining)
    wholesale_red_barrels = list(filter(lambda barrel: barrel.price <= gold_remaining, wholesale_red_barrels))
    print("remaining affordable red barrels:", wholesale_red_barrels)
    if len(wholesale_red_barrels) == 0:
        return list_to_buy
    best_affordable_barrel = min(wholesale_red_barrels, key=lambda barrel: barrel.price/barrel.ml_per_barrel)
    print("best_affordable_barrel:", best_affordable_barrel)
    while gold_remaining >= best_affordable_barrel.price:
        quantity_to_buy = gold_remaining // best_affordable_barrel.price
        list_to_buy.append({"sku": best_affordable_barrel.sku, "quantity": quantity_to_buy})
        print("new state of list:", list_to_buy)
        gold_remaining -= best_affordable_barrel.price * quantity_to_buy
        wholesale_red_barrels[wholesale_red_barrels.index(best_affordable_barrel)].quantity -= quantity_to_buy
        if wholesale_red_barrels[wholesale_red_barrels.index(best_affordable_barrel)].quantity == 0:
            wholesale_red_barrels.remove(best_affordable_barrel)
        best_affordable_barrel = min(wholesale_red_barrels, key=lambda barrel: barrel.price/barrel.ml_per_barrel)

    print("list_to_buy:", list_to_buy)
    return list_to_buy