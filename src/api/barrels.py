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

    #500ml for small barrels (from logs)
    totalml = len(barrels_delivered) * (barrels_delivered[0].ml_per_bottle)
    #100 gold for small barrels (from logs)
    totalgold = len(barrels_delivered) * (barrels_delivered[0].price)

    #if we have enough gold, go through with the purchase
    if(totalgold > barrels_delivered[0].price):
        #add how many ml you just bought
        updateml = f"UPDATE global_inventory SET num_green_ml = (num_green_ml + {totalml})"
        #take away how much gold you just spent
        updategold = f"UPDATE global_inventory SET gold = (gold - {totalgold})"
        #buy 500ml barrels
        with db.engine.begin() as connection:
            resultml = connection.execute(sqlalchemy.text(updateml)).scalar()
            resultgold = connection.execute(sqlalchemy.text(updategold)).scalar()
        
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