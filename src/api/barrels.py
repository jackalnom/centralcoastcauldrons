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
    # Calculate the total ml of green potion delivered
    total_ml_delivered = sum(barrel.ml_per_barrel * barrel.quantity for barrel in barrels_delivered if barrel.sku.startswith("GREEN"))

    with db.engine.begin() as connection:
        sql_to_execute = """
            UPDATE global_inventory
            SET num_green_ml = num_green_ml + :ml_added
        """
        connection.execute(sqlalchemy.text(sql_to_execute), {"ml_added" : total_ml_delivered})

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return {"message": "OK", "total_ml_added": total_ml_delivered}

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    barrel_cost = 100  # Hard coded
    green_ml_per_barrel = 1000  # Hard coded
    plan = []

    with db.engine.begin() as connection:
        sql_to_execute = """
            SELECT num_green_potions, gold FROM global_inventory
        """
        inventory_result = connection.execute(sqlalchemy.text(sql_to_execute))
        for i in inventory_result:
            num_green_potions, gold = i

            if num_green_potions < 10 and gold >= barrel_cost:
                plan.append({
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1,
                })

    return plan


