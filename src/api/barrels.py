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
            price_of_delivery -= barrel.quantity * barrel.price
        if barrel.potion_type == [0, 1, 0, 0]:
            num_green_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery -= barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 1, 0]:
            num_blue_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery -= barrel.quantity * barrel.price
        elif barrel.potion_type == [0, 0, 0, 1]:
            num_dark_ml = barrel.ml_per_barrel * barrel.quantity
            price_of_delivery -= barrel.quantity * barrel.price

    order_type = "barrel"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""INSERT INTO ledgerized_inventory (
                                                        order_id,
                                                        order_type,
                                                        gold,
                                                        num_red_ml,
                                                        num_green_ml,
                                                        num_blue_ml,
                                                        num_dark_ml
                                                    )
                                                    VALUES (:order_id,
                                                            :order_type, 
                                                            :gold, 
                                                            :red_ml, 
                                                            :green_ml, 
                                                            :blue_ml, 
                                                            :dark_ml)
                                                    """),
                                                    [{"order_id": order_id,
                                                      "order_type": order_type,
                                                      "gold": price_of_delivery,
                                                      "red_ml": num_red_ml,
                                                      "green_ml": num_green_ml,
                                                      "blue_ml": num_blue_ml,
                                                      "dark_ml": num_dark_ml}])

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    return "OK"


# Gets called once a day
@router.post("/plan")   # get inventory state to plan purchase of ingredients (ml)
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print("CALLED get_wholesale_purchase_plan()")
    print("Barrel Catalog: ", wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT SUM(li.gold) as gold, 
                                                    SUM(li.num_red_ml) as red_ml, 
                                                    SUM(li.num_green_ml) as green_ml, 
                                                    SUM(li.num_blue_ml) as blue_ml, 
                                                    SUM(li.num_dark_ml) as dark_ml
                                                    FROM ledgerized_inventory as li"""))
    row = result.fetchone()
    gold = row.gold
    red_ml = row.red_ml
    green_ml = row.green_ml
    blue_ml = row.blue_ml
    dark_ml = row.dark_ml

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT ml_capacity
                                                    FROM shop_states"""))
    row = result.fetchone()
    ml_cap = row.ml_capacity

    ml_room = ml_cap - (red_ml + green_ml + blue_ml + dark_ml)

    red_memory = []
    green_memory = []
    blue_memory = []
    dark_memory = []

    # unpack what is in the catalog
    min_price = 100
    max_price = 10000   # drastically large to allow for prices of any type

    if gold < 500:
        max_price = 150 # try to force barrels sold to be small barrels to increase variety

    for sale in wholesale_catalog:
        if sale.potion_type == [1, 0, 0, 0] and max_price >= sale.price and sale.price >= min_price:
            red_memory.append(sale)
        elif sale.potion_type == [0, 1, 0, 0] and max_price >= sale.price and sale.price >= min_price:
            green_memory.append(sale)
        elif sale.potion_type == [0, 0, 1, 0] and max_price >= sale.price and sale.price >= min_price:
            blue_memory.append(sale)
        elif sale.potion_type == [0, 0, 0, 1] and max_price >= sale.price and sale.price >= min_price:
            dark_memory.append(sale)

    dark_in_cat = True
    bootstrap = True
    if gold > 2000:
        bootstrap = False
        budget = (gold * 7) // 10   # budget = 70% of gold
        if dark_memory == []:   # if there are no dark barrels in catalog
            dark_in_cat = False
            budget = budget // 3
        budget = budget // 4        # can spend 25% of budget at a time
    else:
        bootstrap = True
        budget = gold
    
    red_bud = green_bud = blue_bud = dark_bud = budget  # all colors have certain budget

    if not dark_in_cat:
        dark_bud = 0

    red_memory.sort(key=lambda x: x.price, reverse=True)
    green_memory.sort(key=lambda x: x.price, reverse=True)
    blue_memory.sort(key=lambda x: x.price, reverse=True)
    dark_memory.sort(key=lambda x: x.price, reverse=True)

    print(f"budget for each color: {budget}, is dark budget: {dark_in_cat}")
    print(f"red mem: {red_memory}\ngreen mem: {green_memory}\nblue mem: {blue_memory}\ndark mem: {dark_memory}")

    # create wishlist
    # barrel in memory: (sku, price)
    cont = True
    temp_barrel_wishlist = {}
    while (red_bud > 0 or green_bud > 0 or blue_bud > 0 or dark_bud > 0) and ml_room > 0 and cont:
        cont = False
        print(f"red bud: {red_bud}, green bud: {green_bud}, blue bud: {blue_bud}, dark bud: {dark_bud}")
        # select a red barrel
        for i in range(len(red_memory)):
            print("in red loop")
            red_bar = red_memory[i]
            if red_bar.price <= red_bud and red_bar.ml_per_barrel <= ml_room and red_bar.quantity > 0:
                if red_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[red_bar.sku] += 1
                else:
                    temp_barrel_wishlist[red_bar.sku] = 1
                red_bud -= red_bar.price
                if bootstrap:
                    green_bud -= red_bar.price
                    blue_bud -= red_bar.price
                    dark_bud -= red_bar.price
                ml_room -= red_bar.ml_per_barrel
                red_memory[i].quantity -= 1
                cont = True
                break

        # select a green barrel
        for i in range(len(green_memory)):
            print("in green loop")
            green_bar = green_memory[i]
            if green_bar.price <= green_bud and green_bar.ml_per_barrel <= ml_room and green_bar.quantity > 0:
                if green_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[green_bar.sku] += 1
                else:
                    temp_barrel_wishlist[green_bar.sku] = 1
                green_bud -= green_bar.price
                if bootstrap:
                    red_bud -= green_bar.price
                    blue_bud -= green_bar.price
                    dark_bud -= green_bar.price
                ml_room -= green_bar.ml_per_barrel
                green_memory[i].quantity -= 1
                cont = True
                break

        # select a blue barrel
        for i in range(len(blue_memory)):
            print("in blue loop")
            blue_bar = blue_memory[i]
            if blue_bar.price <= blue_bud and blue_bar.ml_per_barrel <= ml_room and blue_bar.quantity > 0:
                if blue_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[blue_bar.sku] += 1
                else:
                    temp_barrel_wishlist[blue_bar.sku] = 1
                blue_bud -= blue_bar.price
                if bootstrap:
                    red_bud -= blue_bar.price
                    green_bud -= blue_bar.price
                    dark_bud -= blue_bar.price
                ml_room -= blue_bar.ml_per_barrel
                blue_memory[i].quantity -= 1
                cont = True
                break

        # select a dark barrel
        for i in range(len(dark_memory)):
            print("in dark loop")
            dark_bar = dark_memory[i]
            if dark_bar.price <= dark_bud and dark_bar.ml_per_barrel <= ml_room and dark_bar.quantity > 0:
                if dark_bar.sku in temp_barrel_wishlist:
                    temp_barrel_wishlist[dark_bar.sku] += 1
                else:
                    temp_barrel_wishlist[dark_bar.sku] = 1
                dark_bud -= dark_bar.price
                if bootstrap:
                    red_bud -= dark_bar.price
                    green_bud -= dark_bar.price
                    blue_bud -= dark_bar.price
                ml_room -= dark_bar.ml_per_barrel
                dark_memory[i].quantity -= 1
                cont = True
                break
    
    print("temp_barrel_wishlist: ", temp_barrel_wishlist)
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

"""
For testing purchase plan:

[
  {
    "sku": "MEDIUM_RED_BARREL",
    "ml_per_barrel": 2500,
    "potion_type": [
      1, 0, 0, 0
    ],
    "price": 250,
    "quantity": 10
  },
  {
    "sku": "SMALL_RED_BARREL",
    "ml_per_barrel": 500,
    "potion_type": [
      1, 0, 0, 0
    ],
    "price": 100,
    "quantity": 10
  },
  {
    "sku": "MINI_GREEN_BARREL",
    "ml_per_barrel": 200,
    "potion_type": [
      0, 1, 0, 0
    ],
    "price": 60,
    "quantity": 1
  },
  {
    "sku": "MEDIUM_GREEN_BARREL",
    "ml_per_barrel": 2500,
    "potion_type": [
      0, 1, 0, 0
    ],
    "price": 250,
    "quantity": 10
  },
  {
    "sku": "SMALL_GREEN_BARREL",
    "ml_per_barrel": 500,
    "potion_type": [
      0, 1, 0, 0
    ],
    "price": 100,
    "quantity": 10
  },
  {
    "sku": "MEDIUM_BLUE_BARREL",
    "ml_per_barrel": 2500,
    "potion_type": [
      0, 0, 1, 0
    ],
    "price": 300,
    "quantity": 10
  },
  {
    "sku": "SMALL_BLUE_BARREL",
    "ml_per_barrel": 500,
    "potion_type": [
      0, 0, 1, 0 
    ],
    "price": 120,
    "quantity": 10
  },
  {
    "sku": "MINI_RED_BARREL",
    "ml_per_barrel": 200,
    "potion_type": [
      1, 0, 0, 0
    ],
    "price": 60,
    "quantity": 10
  },
  {
    "sku": "MINI_BLUE_BARREL",
    "ml_per_barrel": 200,
    "potion_type": [
      0, 0, 1, 0
    ],
    "price": 60,
    "quantity": 1
  },
  {
    "sku": "LARGE_DARK_BARREL",
    "ml_per_barrel": 10000,
    "potion_type": [
      0, 0, 0, 1
    ],
    "price": 750,
    "quantity": 10
  },
  {
    "sku": "LARGE_BLUE_BARREL",
    "ml_per_barrel": 10000,
    "potion_type": [
      0, 0, 1, 0
    ],
    "price": 600,
    "quantity": 30
  },
  {
    "sku": "LARGE_GREEN_BARREL",
    "ml_per_barrel": 10000,
    "potion_type": [
      0, 1, 0, 0 
    ],
    "price": 400,
    "quantity": 30
  },
  {
    "sku": "LARGE_RED_BARREL",
    "ml_per_barrel": 10000,
    "potion_type": [
      1, 0, 0, 0
    ],
    "price": 500,
    "quantity": 30
  }
]
"""