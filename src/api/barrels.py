import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int] #[red, green, blue, dark]
    price: int

    quantity: int


## potion_type:
#  red: potion_type[0] == 1
#  green: potion_type[1] == 1
#  blue: potion_type[2] == 1

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """Barrel Deliverer!"""
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        currentgold = connection.exectute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

        for barrel in barrels_delivered:
            totalml = barrel.quantity * barrel.ml_per_bottle
            totalprice = barrel.quantity * barrel.price

            if currentgold < totalprice:
                print(f"ERROR: Not enough gold! Current gold: {currentgold}, price: {totalprice}")
                return "ERROR!"
            
            update_ml = f"UPDATE global_inventory SET {barrel.sku}_ml = {barrel.sku}_ml + {totalml}"
            update_gold = f"UPDATE global_inventory SET gold = gold - {totalprice}"

            connection.execute(sqlalchemy.text(update_ml))
            connection.execute(sqlalchemy.text(update_gold))

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Planning to purchase barrels"""
    print(wholesale_catalog)

    #sql queries to return number of potions, and gold amount
    #combine
    redpotionqry = "SELECT num_red_potions FROM global_inventory"
    greenpotionqry = "SELECT num_green_potions FROM global_inventory"
    bluepotionqry = "SELECT num_blue_potions FROM global_inventory"
    goldqry = "SELECT gold FROM global_inventory"

    with db.engine.begin() as connection:
        redpotion = connection.execute(sqlalchemy.text(redpotionqry)).scalar()
        greenpotion = connection.execute(sqlalchemy.text(greenpotionqry)).scalar()
        bluepotion = connection.execute(sqlalchemy.text(bluepotionqry)).scalar()
        goldamt = connection.execute(sqlalchemy.text(goldqry)).scalar()

    purchase_plan = []

#have 1 for loop to the catalog
#then have all the if statements go under it

    #check if we need red potions (if we have less than 10)
    if redpotion < 10 and goldamt >= 100:
        for barrel in wholesale_catalog:
            if barrel.potion_type[0] == 1:
                purchase_plan.append({"sku": "SMALL_RED_BARREL", 
                                      "quantity": 1})

    #check if we need green potions (if we have less than 10)
    if greenpotion < 10 and goldamt >= 100:
        for barrel in wholesale_catalog:
            if barrel.potion_type[1] == 1:
                purchase_plan.append({"sku": "SMALL_GREEN_BARREL", 
                                      "quantity": 1})

    #check if we need blue potions (if we have less than 10)
    if bluepotion < 10 and goldamt >= 100:
        for barrel in wholesale_catalog:
            if barrel.potion_type[2] == 1:
                purchase_plan.append({"sku": "SMALL_BLUE_BARREL", 
                                      "quantity": 1})

    return purchase_plan