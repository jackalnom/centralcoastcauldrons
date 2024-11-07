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
#  dark: potion_type[3] == 1

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """Barrel Deliverer!"""
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        currentgold = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM gold_ledgers")).scalar_one()

        for barrel in barrels_delivered:
            totalml = barrel.quantity * barrel.ml_per_barrel
            totalprice = barrel.quantity * barrel.price

            if currentgold < totalprice:
                print(f"ERROR: Not enough gold! Current gold: {currentgold}, price: {totalprice}")
                return "ERROR!"

            updateml = f"INSERT INTO ml_ledgers (num_{barrel.sku}_ml) VALUES ({totalml})"
            connection.execute(sqlalchemy.text(updateml))

            updategold = f"INSERT INTO gold_ledgers (gold_change) VALUES (-{totalprice})"
            connection.execute(sqlalchemy.text(updategold))

            currentgold -= totalprice

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Planning to purchase barrels"""
    print(wholesale_catalog)

    #collect current amount of ml of each base color, and gold
    redmlqry = "SELECT SUM(num_red_ml) AS current_red_ml FROM ml_ledgers"
    greenmlqry = "SELECT SUM(num_green_ml) AS current_green_ml FROM ml_ledgers"
    bluemlqry = "SELECT SUM(num_blue_ml) AS current_blue_ml FROM ml_ledgers"
    darkmlqry = "SELECT SUM(num_dark_ml) AS current_dark_ml FROM ml_ledgers"

    goldqry = "SELECT SUM(gold_change) AS num_gold FROM gold_ledgers"

    with db.engine.begin() as connection:
        redml = connection.execute(sqlalchemy.text(redmlqry)).scalar()
        greenml = connection.execute(sqlalchemy.text(greenmlqry)).scalar()
        blueml = connection.execute(sqlalchemy.text(bluemlqry)).scalar()
        darkml = connection.execute(sqlalchemy.text(darkmlqry)).scalar()

        goldamt = connection.execute(sqlalchemy.text(goldqry)).scalar()

    print(f"""redml: {redml} greenml: {greenml} blueml: {blueml} darkml: {darkml} gold: {goldamt}""")

    purchase_plan = []

    for barrel in wholesale_catalog:
        #check if we need to buy red barrels (if we have less than 500 red ml)
        if barrel.potion_type[0] == 1 and redml < 500 and goldamt >= barrel.price:
            purchase_plan.append({"sku": barrel.sku, "quantity": 1})
            goldamt -= barrel.price
            redml += barrel.ml_per_barrel

        if barrel.potion_type[1] == 1 and greenml < 500 and goldamt >= barrel.price:
            purchase_plan.append({"sku": barrel.sku, "quantity": 1})
            goldamt -= barrel.price
            redml += barrel.ml_per_barrel

        if barrel.potion_type[2] == 1 and blueml < 500 and goldamt >= barrel.price:
            purchase_plan.append({"sku": barrel.sku, "quantity": 1})
            goldamt -= barrel.price
            redml += barrel.ml_per_barrel
                    
        if barrel.potion_type[3] == 1 and darkml < 500 and goldamt >= barrel.price:
            purchase_plan.append({"sku": barrel.sku, "quantity": 1})
            goldamt -= barrel.price
            redml += barrel.ml_per_barrel

    return purchase_plan