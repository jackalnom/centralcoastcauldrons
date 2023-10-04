from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.api import database as db

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
        inventory = db.get_global_inventory()
        money_spent = barrel.price * barrel.quantity
        ml_gained = barrel.ml_per_barrel * barrel.quantity
        new_gold = inventory["gold"] - money_spent
        new_red_ml = inventory["num_red_ml"] + ml_gained
        update_command = f"UPDATE global_inventory SET gold = {new_gold}, num_red_ml = {new_red_ml} WHERE id = 1"
        db.execute(update_command)

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    # if we have the gold for it and we have less than so many options,
    # purchasing a small red barrel
    catalog = {barrel.sku: barrel for barrel in wholesale_catalog}
    if "SMALL_RED_BARREL" not in catalog:
        print("not buying anything, no red small red barrels")
        return
    inventory = db.get_global_inventory()
    num_potions = inventory["num_red_potions"]
    if num_potions >= 10:
        print("not buying, we already have at least 10 red potions")
        return

    # much as much ml we can afford or as they have
    gold = inventory["gold"]
    small_barrels = catalog["SMALL_RED_BARREL"]
    max_afforded = gold // small_barrels.price
    barrels_available = small_barrels.quantity
    barrels_to_buy = min(max_afforded, barrels_available)
    if barrels_to_buy <= 0:
        print("not buying, can't afford any barrels")
        return

    print(f"purchasing {barrels_to_buy} barrels at {small_barrels.price}")

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": barrels_to_buy,
        }
    ]
