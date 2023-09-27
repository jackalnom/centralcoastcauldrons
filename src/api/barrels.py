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

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    ## Start new implimentation
    for indiv_barrel in barrels_delivered:
        if(indiv_barrel.potion_type == [0]):
            ml_total_delivered = indiv_barrel.quantity*indiv_barrel.ml_per_barrel
            cost_total = indiv_barrel.quantity*indiv_barrel.price
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            for row in result:
                current_red_ml = row[2] + ml_total_delivered
                current_gold = row[3] - cost_total
            result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {current_red_ml}"))
            result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {current_gold}"))

    ## end new implimentation 
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # Start new implimentation

    for for_sale in wholesale_catalog:  # go through catalog
        if for_sale.sku == "SMALL_RED_BARREL":
            # only buy small red for now

            # check current inventory
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            
            for row in result:
                current_gold = row[3]
                current_red_potion = row[1]
            
            # just buy maximum number of barrels
            max_barrel = min(current_gold // for_sale.price, for_sale.quantity)
            
            # only buy if stock is below 10
            if current_red_potion < 10:
                return [
                    {
                        "sku": "SMALL_RED_BARREL",
                        "quantity": max_barrel,
                    }
                ]
    
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 0,
        }
    ]
