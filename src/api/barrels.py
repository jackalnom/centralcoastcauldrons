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

@router.post("/deliver/{order_id}") # update inventory based on order to get ingredients (ml)
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    print("CALLED post_deliver_barrels()")
    price_of_delivery = num_green_ml = num_red_ml = num_blue_ml = num_dark_ml = 0

    for barrel in barrels_delivered:
        if barrel.potion_type == [1, 0, 0, 0]:
            num_red_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        if barrel.potion_type == [0, 1, 0, 0]:
            num_green_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 1, 0]:
            num_blue_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 0, 1]:
            num_dark_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery += barrel.quantity * barrel.price
        # print("type:", barrel.potion_type)
    # print(f"red: {num_red_ml}, green: {num_green_ml}, blue: {num_blue_ml}, dark: {num_dark_ml}")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""UPDATE global_inventory 
                                                    SET num_red_ml = num_red_ml + :num_red_ml, 
                                                    num_green_ml = num_green_ml + :num_green_ml, 
                                                    num_blue_ml = num_blue_ml + :num_blue_ml, 
                                                    num_dark_ml = num_dark_ml + :num_dark_ml, 
                                                    gold = gold - :price_of_delivery"""), 
                                                    [{"num_red_ml": num_red_ml,
                                                      "num_green_ml": num_green_ml,
                                                      "num_blue_ml": num_blue_ml,
                                                      "num_dark_ml": num_dark_ml,
                                                      "price_of_delivery": price_of_delivery}])

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    return "OK"


# Gets called once a day
@router.post("/plan")   # get inventory state to plan purchase of ingredients (ml)
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print("CALLED get_wholesale_purchase_plan()")
    print("Barrel Catalog: ", wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    row = result.fetchone()
    num_red = row.num_red_ml
    num_green = row.num_green_ml
    num_blue = row.num_blue_ml
    num_dark = row.num_dark_ml
    gold = row.gold

    ml_room = row.ml_capacity - (num_red + num_green + num_blue + num_dark)

    red_memory = []
    green_memory = []
    blue_memory = []
    dark_memory = []

    # unpack what is in the catalog
    for sale in wholesale_catalog:
        if sale.potion_type == [1, 0, 0, 0]:
            red_memory.append(sale)
        elif sale.potion_type == [0, 1, 0, 0]:
            green_memory.append(sale)
        elif sale.potion_type == [0, 0, 1, 0]:
            blue_memory.append(sale)
        elif sale.potion_type == [0, 0, 0, 1]:
            dark_memory.append(sale)

    dark_in_cat = True
    if row.gold > 2000:
        budget = (gold * 7) // 10   # budget = 70% of gold
        if dark_memory == []:   # if there are no dark barrels in catalog
            dark_in_cat = False
            budget = budget // 3
        budget = budget // 4        # can spend 25% of budget at a time
    else:
        budget = gold
    
    red_bud = green_bud = blue_bud = dark_bud = budget  # all colors have certain budget

    if not dark_in_cat:
        dark_bud = 0

    red_memory.sort(key=lambda x: x.price, reverse=True)
    green_memory.sort(key=lambda x: x.price, reverse=True)
    blue_memory.sort(key=lambda x: x.price, reverse=True)
    dark_memory.sort(key=lambda x: x.price, reverse=True)

    # create wishlist
    # barrel in memory: (sku, price)
    cont = True
    temp_barrel_wishlist = {}
    while (red_bud > 0 or green_bud > 0 or blue_bud > 0 or dark_bud > 0) and ml_room > 0 and cont:
        cont = False
        # select a red barrel
        for i in range(len(red_memory)):
            red_bar = red_memory[i]
            if red_bar.price <= red_bud and red_bar.ml_per_barrel <= ml_room and budget >= red_bar.price:
                if red_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[red_bar.sku] += 1
                else:
                    temp_barrel_wishlist[red_bar.sku] = 1
                red_bud -= red_bar.price
                budget -= red_bar.price     # precautionary step
                ml_room -= red_bar.ml_per_barrel
                red_memory[i].quantity -= 1
                cont = True
                break

        # select a green barrel
        for i in range(len(green_memory)):
            green_bar = green_memory[i]
            if green_bar.price <= green_bud and green_bar.ml_per_barrel <= ml_room and budget >= red_bar.price:
                if green_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[green_bar.sku] += 1
                else:
                    temp_barrel_wishlist[green_bar.sku] = 1
                green_bud -= green_bar.price
                budget -= green_bar.price     # precautionary step
                ml_room -= green_bar.ml_per_barrel
                green_memory[i].quantity -= 1
                cont = True
                break

        # select a blue barrel
        for i in range(len(blue_memory)):
            blue_bar = blue_memory[i]
            if blue_bar.price <= blue_bud and blue_bar.ml_per_barrel <= ml_room and budget >= red_bar.price:
                if blue_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[blue_bar.sku] += 1
                else:
                    temp_barrel_wishlist[blue_bar.sku] = 1
                blue_bud -= blue_bar.price
                budget -= blue_bar.price     # precautionary step
                ml_room -= blue_bar.ml_per_barrel
                blue_memory[i].quantity -= 1
                cont = True
                break

        # select a dark barrel
        for i in range(len(dark_memory)):
            dark_bar = dark_memory[i]
            if dark_bar.price <= dark_bud and dark_bar.ml_per_barrel <= ml_room and budget >= red_bar.price:
                if dark_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[dark_bar.sku] += 1
                else:
                    temp_barrel_wishlist[dark_bar.sku] = 1
                dark_bud -= dark_bar.price
                budget -= dark_bar.price     # precautionary step
                ml_room -= dark_bar.ml_per_barrel
                dark_memory[i].quantity -= 1
                cont = True
                break
    
    keys, values = temp_barrel_wishlist.keys(), temp_barrel_wishlist.values()
    keys = list(keys)
    values = list(values)
    purchase_plan = []
    for i in range(len(values)):
        if values[i] > 0:
            purchase_plan.append({
                "sku": keys[i],
                "quantity": values[i]
            })

    print("Barrel Purchase Plan:", purchase_plan)

    return purchase_plan

