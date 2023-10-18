from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api.database import engine as db
from src.api.models import Inventory
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


def deliver_barrels(barrels_delivered: list[Barrel],gold, num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml):
    for barrel in barrels_delivered:
        match barrel.potion_type:
            case [1,0,0,0]:
                num_red_ml += barrel.quantity * barrel.ml_per_barrel
                gold -=  barrel.price
            case [0,1,0,0]:
                num_green_ml += barrel.quantity * barrel.ml_per_barrel
                gold_left -= barrel.price
            case [0,0,1,0]:
                num_blue_ml += barrel.quantity * barrel.ml_per_barrel
                gold_left -= barrel.price
            case [0,0,0,1]:
                pass
            case _:
                raise Exception("Invalid potion type")
    return gold, num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml
    


@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    inventory.set_inventory(*deliver_barrels(barrels_delivered,*inventory.get_inventory()))
    inventory.sync()
    print(inventory.get_inventory())
    return "OK"

    
def get_orders(wholesale_catalog: list[Barrel],gold,num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml):
    orders = []
    gold_left = gold
    for barrel in wholesale_catalog:
        match barrel.potion_type:
            case [1,0,0,0] if gold_left >=  barrel.price:
                num_red_ml += 1 * barrel.ml_per_barrel
                gold_left -= barrel.price
                barrel.quantity = 1
                orders.append(barrel)
            case [0,1,0,0] if gold_left >=barrel.price:
                num_green_ml += 1 * barrel.ml_per_barrel
                gold_left -= barrel.price
                barrel.quantity = 1
                orders.append(barrel)
            case [0,0,1,0] if gold_left >= barrel.price:
                num_blue_ml += 1 * barrel.ml_per_barrel
                gold_left -=  barrel.price
                barrel.quantity = 1
                orders.append(barrel)
            case [0,0,0,1]:
                pass
            case _:
                print(barrel)
    return orders


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    return get_orders(wholesale_catalog,*inventory.get_inventory())

        

