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
    print("CALLED post_deliver_barrels()")
    price_of_delivery = num_green_ml = num_red_ml = num_blue_ml = num_dark_ml = 0

    for barrel in barrels_delivered:
        if barrel.potion_type == [1, 0, 0, 0]:
            num_red_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        if barrel.potion_type == [0, 1, 0, 0]:
            num_green_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 1, 0]:
            num_blue_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 0, 1]:
            num_dark_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        print("type:", barrel.potion_type)
    print(f"red: {num_red_ml}, green: {num_green_ml}, blue: {num_blue_ml}, dark: {num_dark_ml}")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""UPDATE global_inventory 
                                                    SET num_red_ml = num_red_ml + :num_red_ml, 
                                                    num_green_ml = num_green_ml + :num_green_ml, 
                                                    num_blue_ml = num_blue_ml + :num_blue_ml, 
                                                    num_dark_ml = num_dark_ml + :num_dark_ml, 
                                                    gold = gold - :price_of_delivery"""), 
                                                    [{"num_red_ml": num_red_ml,
                                                      "num_green_ml": num_green_ml,
                                                      "num_blue_ml": num_blue_ml,
                                                      "num_dark_ml": num_dark_ml,
                                                      "price_of_delivery": price_of_delivery}])

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    return "OK"


# Gets called once a day
@router.post("/plan")   # get inventory state to plan purchase of ingredients (ml)
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print("CALLED get_wholesale_purchase_plan()")
    res = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_red_potions, num_blue_potions, gold FROM global_inventory"))
    row = result.fetchone()
    num_green_p = row[0]
    num_red_p = row[1]
    num_blue_p = row[2]
    gold = row[3]
    for sale in wholesale_catalog:
        if sale.sku == "SMALL_GREEN_BARREL":
            quantity = 0
            if num_green_p < 2 and gold >= sale.price:
                quantity = 1 
            if quantity > 0:
                res.append({
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": quantity
                })
                gold -= sale.price
        elif sale.sku == "SMALL_RED_BARREL":
            quantity = 0
            if num_red_p < 2 and gold >= sale.price:
                quantity = 1
            if quantity > 0:
                res.append({
                    "sku": "SMALL_RED_BARREL",
                    "quantity": quantity
                })
                gold -= sale.price
        elif sale.sku == "SMALL_BLUE_BARREL":
            quantity = 0
            if num_blue_p < 2 and gold >= sale.price:
                quantity = 1
            if quantity > 0:
                res.append({
                    "sku": "SMALL_BLUE_BARREL",
                    "quantity": quantity
                }) 
                gold -= sale.price

    print("Barrel Catalog: ", wholesale_catalog)
    print("Barrel Purchase Plan:", res)

    return res

