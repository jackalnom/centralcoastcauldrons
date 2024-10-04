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
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        currentgoldsql = "SELECT gold FROM global_inventory"
        currentgold = connection.execute(sqlalchemy.text(currentgoldsql)).scalar_one()
        #500ml for small barrels (from logs)
        totalml = barrels_delivered[0].quantity * (barrels_delivered[0].ml_per_barrel)
        #100 gold for small barrels (from logs)
        totalprice = barrels_delivered[0].quantity * (barrels_delivered[0].price)

        #if we have enough gold, go through with the purchase
        if(currentgold < totalprice):
            print(f"DANGER DANGER THIS SHOULD NEVER HAPPEN, currentgold {currentgold}, buying {totalprice}")
            return "ERROR"

        print(f"updating inventory from barrels delivered, adding {totalml} ml, subtracting {totalprice} gold")
        #add how many ml you just bought
        updateml = f"UPDATE global_inventory SET num_green_ml = (num_green_ml + {totalml})"
        #take away how much gold you just spent
        updategold = f"UPDATE global_inventory SET gold = (gold - {totalprice})"
        #buy 500ml barrels

        connection.execute(sqlalchemy.text(updateml))
        connection.execute(sqlalchemy.text(updategold))
        
    
        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    #sql statements as strings
    greenpotionqry = "SELECT num_green_potions FROM global_inventory"
    goldqry = "SELECT gold FROM global_inventory"
    mlqry = "SELECT num_green_ml FROM global_inventory"

    with db.engine.begin() as connection:
        greenpotion = connection.execute(sqlalchemy.text(greenpotionqry)).scalar()
        goldamt = connection.execute(sqlalchemy.text(goldqry)).scalar()
        mlamt = connection.execute(sqlalchemy.text(mlqry)).scalar()

    #if we have less than 10 potions, buy some
    if(greenpotion < 10 and goldamt >= 100):
        return [{"sku": "SMALL_GREEN_BARREL",
            "quantity": 1}]
        
    return []