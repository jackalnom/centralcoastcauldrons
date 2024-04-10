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

@router.post("/deliver/{order_id}") # update inventory based on order to get ingredients (ml)
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):

    for barrel in barrels_delivered:
        ml_of_potion_delivery = barrel.ml_per_barrel * barrel.quantity
        price_of_delivery = barrel.quantity * barrel.price

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {ml_of_potion_delivery}, gold = gold - {price_of_delivery}"))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    return "OK"


# Gets called once a day
@router.post("/plan")   # get inventory state to plan purchase of ingredients (ml)
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    res = []

    for sale in wholesale_catalog:
        if sale.sku == "SMALL_GREEN_BARREL":
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text(f"SELECT num_green_potions, gold FROM global_inventory"))
            for row in result:
                num_potions = row[0]
                gold = row[1]
                quantity = 0
                if num_potions < 10 and gold >= sale.price:
                    quantity += 1 
                if quantity > 0:
                    res.append({
                        "sku": "SMALL_GREEN_BARREL",
                        "quantity": quantity
                    })

    print(wholesale_catalog)

    # return [
    #     {
    #         "sku": "SMALL_RED_BARREL",
    #         "quantity": 1,
    #     }
    # ]

    return res

