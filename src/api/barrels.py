from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.api.database import engine as db
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
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    num_red_potions, num_red_ml, gold= result.fetchone()

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            if barrel.sku == "SMALL_RED_BARREL":
                num_red_potions += barrel.quantity
                num_red_ml += barrel.quantity * barrel.ml_per_barrel
                gold -= barrel.quantity * barrel.price
            else:
                return "INVALID SKU"
            
    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :num_red_potions, num_red_ml = :num_red_ml, gold = :gold"), num_red_potions=num_red_potions, num_red_ml=num_red_ml, gold=gold)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        num_red_potions, _, gold= result.fetchone()
        if num_red_potions < 10:
            for barre_catalog in wholesale_catalog:
                if barre_catalog.sku == "SMALL_RED_BARREL" and barre_catalog.price * barre_catalog.quantity < gold:
                    return [
                        {
                            "sku": "SMALL_RED_BARREL",
                            "quantity": barre_catalog.quantity,
                        }
                    ]

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]
