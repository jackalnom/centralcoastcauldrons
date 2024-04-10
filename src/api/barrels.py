from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
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

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        for barrel in barrels_delivered:
            if barrel.potion_type == [0, 1, 0, 0]:
                current_ml = row["num_green_ml"]
                current_gold = row["gold"]
                sql_to_execute = f"UPDATE global_inventory SET num_green_ml = {current_ml + (barrel.ml_per_barrel * barrel.quantity)}, gold = {current_gold - (barrel.price * barrel.quantity)}"
                connection.execute(sqlalchemy.text(sql_to_execute))
            sql_to_execute = f"INSERT INTO barrel_purchases (sku, quantity) VALUES ('{barrel.sku}', {barrel.quantity})"
            connection.execute(sqlalchemy.text(sql_to_execute))
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    sql_to_execute = "SELECT * FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        row = result.fetchone()._asdict()
        barrels_to_purchase = []
        for barrel in wholesale_catalog:
            if barrel.potion_type == [0, 1, 0, 0]:
                if row["num_green_potions"] < 10:
                    barrels_to_purchase.append(barrel)
            # elif barrel.potion_type == [1, 0, 0, 0]:
            #     if row["num_red_potions"] < 10:
            #         barrels_to_purchase.append(barrel)
            # elif barrel.potion_type == [0, 0, 1, 0]:
            #     if row["num_blue_potions"] < 10:
            #         barrels_to_purchase.append(barrel)
        current_green_barrel = None
        # current_red_barrel = None
        # current_blue_barrel = None
        green_running_total = 0
        red_running_total = 0
        blue_running_total = 0
        print(barrels_to_purchase)
        print(row["gold"])
        for barrel in barrels_to_purchase:
            if red_running_total + blue_running_total + barrel.price <= row["gold"]:
                if barrel.potion_type == [0, 1, 0, 0]:
                    if current_green_barrel:
                        print("reached green barrel comparison")
                        if barrel.ml_per_barrel > current_green_barrel.ml_per_barrel:
                            green_running_total += barrel.price
                            green_running_total -= current_green_barrel.price
                            current_green_barrel = barrel
                    else:
                        current_green_barrel = barrel
                # elif barrel.potion_type == [1, 0, 0, 0]:
                #     current_red_barrel = barrel
                # elif barrel.potion_type == [0, 0, 1, 0]:
                #     current_blue_barrel = barrel
        purchase_plan = []
        if current_green_barrel:
            purchase_plan.append(
                {
                    "sku": current_green_barrel.sku,
                    "quantity": 1,
                }
            )
        return purchase_plan