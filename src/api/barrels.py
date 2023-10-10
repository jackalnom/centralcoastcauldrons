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
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()

            if barrel.sku == "SMALL_RED_BARREL":
                num_red_ml += barrel.quantity * barrel.ml_per_barrel
                gold -= barrel.quantity * barrel.price
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:num_red_ml, gold=:gold"),{"num_red_ml":num_red_ml,"gold": gold})
            elif barrel.sku == "SMALL_BLUE_BARREL":

                num_blue_ml += barrel.quantity * barrel.ml_per_barrel
                gold -= barrel.quantity * barrel.price
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml=:num_blue_ml, gold=:gold"),{"num_blue_ml":num_blue_ml,"gold": gold})

            elif barrel.sku == "SMALL_GREEN_BARREL":

                num_green_potions += barrel.quantity
                num_green_ml += barrel.quantity * barrel.ml_per_barrel
                gold -= barrel.quantity * barrel.price
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET  num_green_ml=:num_green_ml, gold=:gold"),{"num_green_ml": num_green_ml, "gold": gold})

            else:
                return "INVALID SKU"
            

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

        num_red_potions, num_red_ml, gold, num_blue_potions,num_blue_ml,id,num_green_potions,num_green_ml= result.fetchone()
        print(result.fetchone())
        orders = []
        gold_left = gold
        if num_red_potions < 10:
            for barre_catalog in wholesale_catalog:
                if barre_catalog.sku == "SMALL_RED_BARREL" and barre_catalog.price * barre_catalog.quantity < gold_left:
                    print("test")
                    orders += [
                        {
                            "sku": "SMALL_RED_BARREL",
                            "quantity": barre_catalog.quantity // 3 + 1,
                        }
                    ]
                    gold_left -=  (barre_catalog.quantity // 3 + 1) * barre_catalog.price
        if num_blue_potions < 10:
            for barre_catalog in wholesale_catalog:
                if barre_catalog.sku == "SMALL_BLUE_BARREL" and barre_catalog.price * barre_catalog.quantity < gold_left:
                    orders+= [
                        {
                            "sku": "SMALL_BLUE_BARREL",
                            "quantity": barre_catalog.quantity // 3 + 1,
                        }
                    ]
                    gold_left -=  (barre_catalog.quantity // 3) * barre_catalog.price

        if num_green_potions < 10:
            for barre_catalog in wholesale_catalog:
                if barre_catalog.sku == "SMALL_GREEN_BARREL" and barre_catalog.price * barre_catalog.quantity < gold_left:
                    orders+= [
                        {
                            "sku": "SMALL_GREEN_BARREL",
                            "quantity": barre_catalog.quantity // 3 + 1,
                        }
                    ]
                    gold_left -=  (barre_catalog.quantity // 3 + 1) * barre_catalog.price

    return orders
