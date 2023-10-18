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
    # add entries as more barrels are desired
    delivery_dict = {
        0: "red",
        1: "green",
        2: "blue",
        3: "dark"
    }
    for indiv_barrel in barrels_delivered:
        ml_total_delivered=0
        cost_total=0

        color = delivery_dict.get(indiv_barrel.potion_type.index(1))
        
        ml_total_delivered = indiv_barrel.quantity*indiv_barrel.ml_per_barrel
        cost_total = indiv_barrel.quantity*indiv_barrel.price

        db.update_gold(-cost_total, f"Delivery of {ml_total_delivered}mL {color}")
        db.update_ml(ml_total_delivered, color, f"Delivery of {ml_total_delivered}mL {color}")
        
        print(f"Delivery taken of {ml_total_delivered}mL of {color} potion, at cost of {cost_total}.")
    
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    #----------------------------------
    # -- Log Barrels -- 
    #----------------------------------
    print("Logging current barrels for sale...")
    # Create new session ID
    with db.engine.begin() as connection:
        catalog_id_result = connection.execute(sqlalchemy.text(f"INSERT INTO barrels_sessions \
                                                                 DEFAULT VALUES  \
                                                                 RETURNING catalog_id"))
        catalog_id =catalog_id_result.first()[0]

    # Go through and log all barrels for sale
    for barrel in wholesale_catalog:
        with db.engine.begin() as connection:
            # check if sku exists in table already
            sku_exist_result = connection.execute(sqlalchemy.text(f"SELECT COUNT(sku) \
                                                                    FROM barrels_catalog \
                                                                    WHERE sku = '{barrel.sku}'"))
        if not sku_exist_result.first()[0]:
            # if not create entry
            sql_getid = f"INSERT INTO barrels_catalog \
                          (sku, ml_per_barrel) \
                          VALUES ('{barrel.sku}', {barrel.ml_per_barrel}) \
                          RETURNING barrel_id"
        else:
            sql_getid = f"SELECT barrel_id \
                          FROM barrels_catalog \
                          WHERE sku = '{barrel.sku}'"

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_getid))
        barrel_id = result.first()[0]

        # Now log actual price for tracking
        with db.engine.begin() as connection:
            # check if sku exists in table already
            sku_exist_result = connection.execute(sqlalchemy.text(f"INSERT INTO barrels_history \
                                                                    (catalog_id, barrel_id, cost, quantity) \
                                                                    VALUES ({catalog_id}, {barrel_id}, {barrel.price}, {barrel.quantity})"))
    #----------------------------------
    # -- Build Purchasing Strategy -- 
    #----------------------------------
    print("Building purchase strategy...")
    # get current potion stock levels

    with db.engine.begin() as connection:
        check_stock_result = connection.execute(sqlalchemy.text(
            "SELECT \
            potion_inventory.type_red, \
            potion_inventory.type_green, \
            potion_inventory.type_blue, \
            potion_inventory.type_dark, \
            CAST(SUM(d_quan) AS INTEGER) AS total \
            FROM potion_inventory \
            join potion_ledger on potion_ledger.potion_id = potion_inventory.id \
            GROUP BY potion_inventory.id"))

    total_stock = [0,0,0,0]
    for potion in check_stock_result:
        quantity = potion[-1]
        total_stock = [x + c*quantity for x, c in zip(total_stock, potion[:-1])]
    
    current_ml = db.get_all_ml()

    NUM_GOLD = db.get_gold()
    gold_left = NUM_GOLD
    total_stock = [x + cml for x, cml in zip(total_stock, current_ml[:-1])]

    # create list of priority to purchase
    potion_stock = [
        {'name': 'RED', 'amount': total_stock[0]},
        {'name': 'GREEN', 'amount': total_stock[1]},
        {'name': 'BLUE', 'amount': total_stock[2]},
        {'name': 'DARK', 'amount': total_stock[3]}
    ]
    # sort based on lowest stock level (will evenly purchase potions)
    # this stragetgy, combined with bottling stragegy should evenly purchase colors
    potion_stock.sort(key=lambda x:x['amount'])
    
    TARGET_STOCK = 3000 # make this dynamic later, maybe 120% of previous day potions idk, this is currently enough for full potion inventory with some margin
    
    #----------------------------------
    # -- Build Purchase Plan -- 
    #----------------------------------
    print("Constructing plan...")
    purchase_plan = []
    # go down colors by priority
    for potion_type in potion_stock:
        barrels_of_color = []
        color = potion_type['name']
        # get barrels of given color
        for barrel in wholesale_catalog:
            if color in barrel.sku:
                # barrel is now being checked, remove from catalog
                if ("MINI" in barrel.sku or "SMALL" in barrel.sku) and color != "DARK":
                    continue
                else:
                    barrels_of_color += [barrel]
                    #wholesale_catalog.remove(barrel)
        
        # sort by largest since those are best value for money
        # want to spend 50% of current gold, or 100, whichever is more
        max_spend = min(gold_left, max((NUM_GOLD)//2, 250))
        print(f"Max Spend is {max_spend}")
        if max_spend < 250:
           
            # dont buy smaller than medium
            break
        barrels_of_color.sort(key=lambda x:x.ml_per_barrel, reverse=True)
        for barrel in barrels_of_color:
            max_num = min(max_spend // barrel.price, barrel.quantity)
            if max_num > 0:
                # add to plan
                max_spend -= (max_num*barrel.price)
                gold_left -= (max_num*barrel.price)
                purchase_plan += [{
                        "sku": f"{barrel.sku}",
                        "quantity": max_num,
                    }]
                # buy max amount of largest possible barrel then break, dont need to buy smalls/minis if not needed
                break

    return purchase_plan