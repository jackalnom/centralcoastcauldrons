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
    colors = ["red", "green", "blue"]
    for barrel in barrels_delivered:
        # getting color
        color = None
        for i in range(len(colors)):
            if barrel.potion_type[i] == 1:
                color = colors[i]
                break

        inventory = db.get_global_inventory()
        money_spent = barrel.price * barrel.quantity
        ml_gained = barrel.ml_per_barrel * barrel.quantity
        new_gold = inventory["gold"] - money_spent
        new_ml = inventory[f"num_{color}_ml"] + ml_gained
        update_command = f"UPDATE global_inventory SET gold = {new_gold}, num_{color}_ml = {new_ml} WHERE id = 1"
        db.execute(update_command)

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    # if we have the gold for it and we have less than so many options,
    # purchasing a small red barrel
    BARRELS_TO_BUY = {
        "SMALL_RED_BARREL",
        "SMALL_BLUE_BARREL",
        "SMALL_GREEN_BARREL",
    }

    # goal is to keep a balance of potion types
    catalog = {
        barrel.sku: barrel
        for barrel in wholesale_catalog
        if barrel.sku in BARRELS_TO_BUY
    }

    inventory = db.get_global_inventory()
    # getting a count of how many potions we have
    colors = ["red", "green", "blue"]
    colors = colors.filter(lambda color: f"SMALL_{color.upper()}_BARREL" in catalog)
    potion_counts = {color: inventory[f"num_{color}_potions"] for color in colors}
    fluid_counts = {color: inventory[f"num_{color}_ml"] for color in colors}

    # if we have have 350ml of red fluid, we might as well have 3.5 red potions
    for color, num_ml in fluid_counts.items():
        potion_counts[color] += num_ml / 100

    # buying the potion we have the least of till we're out of money
    i = 0
    gold = inventory["gold"]
    purchase_plan = {}

    while i < len(colors):
        if i == 0:  # recomputing the order when we reset
            buying_order = colors.sort(lambda color: potion_counts[color])
        color_to_buy = buying_order[i]
        barrel = catalog[f"SMALL_{color_to_buy.upper()}_BARREL"]
        can_afford = gold >= barrel.price
        if can_afford:
            # adding to purchase plan
            potion_counts += barrel.ml_per_barrel / 100
            purchase_plan[color_to_buy] = purchase_plan.get(color_to_buy, 0) + 1
            gold -= barrel.price
            i = 0
        else:
            i += 1

    # getting a return value
    ans = []
    for color, count in purchase_plan.items():
        sku = f"SMALL_{color_to_buy.upper()}_BARREL"
        barrel = catalog[sku]
        print(f"purchasing {count} color barrels at {barrel.price}")
        ans.append(
            {
                "sku": sku,
                "quantity": count,
            }
        )

    return ans
