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

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    mls_delivered = 0 
    total_gold = 0 
    if (len(barrels_delivered) == 0):
        raise("No barrels sent in API")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_green_ml 
            FROM global_inventory
            WHERE id = 1
        """))
        if (not (result := result.first())):
            print("Server Error")
            raise("/deliver/{order_id} error with DB")
        
        # check if we have sufficient mls to send
        for barrel in barrels_delivered:
            if (barrel.price < 0):
                continue
            mls_delivered += barrel.quantity + barrel.ml_per_barrel
            total_gold += barrel.quantity * barrel.price
        if (result[0] < mls_delivered):
            print("Insufficient mls.")
            return "NOPE"
        # update DB to take into account barrelt that were delivered
        # update gold that was recieved
        connection.execute(sqlalchemy.text(f"""
            UPDATE global_inventory 
            SET num_green_ml = num_green_ml - {mls_delivered}, 

            gold = gold + {total_gold}
        """))
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    num_green = None
    gold = None
    quantity = None
    # as per docs, buy one GREEN_BARREL if we are short
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""
            SELECT num_green_potions, gold 
            FROM global_inventory
            WHERE id = 1
        """))
        if (not (result := result.first())):
            print('Id not found.')
            return []
        num_green = result[0]
        gold = result[1]
        if (num_green < 10):
            # find green barrel within catalog
            for barrel in wholesale_catalog:
                if barrel.sku == "SMALL_GREEN_BARREL" and \
                    barrel.quantity >= 1:
                    
                    # get price and purhcase 1 if we have enough
                    price = barrel.price
                    if (gold < price):
                        print("Insufficient gold.")
                        return []
                    # update db to take into account price and increase in ml
                    # TODO: take into accout how much we purchased
                    ml_gained = barrel.ml_per_barrel
                    print("purchased green barrel")
                    connection.execute(sqlalchemy.text(f"""
                        UPDATE global_inventory 
                        SET gold = gold - {price}, 
                        num_green_ml = num_green_ml + {ml_gained}
                    """))
                    return [
                        {
                            "sku": "SMALL_GREEN_BARREL",
                            "quantity" : 1
                        }
                    ]
                    
    
    print(wholesale_catalog)

    return [
    ]

