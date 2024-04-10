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
        quantity = 0
        sku = ""
        for barrel in wholesale_catalog:
            if barrel.potion_type == [0, 1, 0, 0]:
                if row["num_green_potions"] < 10:
                    if barrel.price <= row["gold"]:
                        quantity = 1
                        sku = barrel.sku
        if quantity == 0:
            return []
        return [
            {
                "sku": sku,
                "quantity": quantity,
            }
        ]