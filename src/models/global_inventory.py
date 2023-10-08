#This class should represent the global inventory of the game
import sqlalchemy
from src import database as db
import math
from pydantic import BaseModel
from sqlalchemy.sql import text
from .transaction import Transaction
from .retail_inventory import RetailInventory
from .wholesale_inventory import WholesaleInventory

#CURRENT INVENTORY
# num_red_potions: 30
# num_red_ml: 0
# gold: 2800



class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


class GlobalInventory:
    #these are temporary placeholders to acccount for decreased functionality
    table_name = "global_inventory"
    red_potion_sku = "RED_POTION_0"
    red_potion_barrel_sku = "SMALL_RED_BARREL"
    price_of_red_potion = 50
    singleton = None
    def __init__(self, id: int, created_at, num_red_potions: int, num_red_ml: int, gold: int):
        self.id = id
        self.created_at = created_at
        self.num_red_potions = num_red_potions
        self.num_red_ml = num_red_ml
        self.gold = gold

        print("GlobalInventory created", self)

    
    @staticmethod
    def get_singleton():

            #check to see if there is a row in the table

        sql_to_execute = text(f"SELECT * FROM {GlobalInventory.table_name} LIMIT 1")

        with db.engine.begin() as connection:
            result = connection.execute(sql_to_execute)
            row = result.fetchone()

        if row is not None:
            # If a row exists, set the singleton to that row
            GlobalInventory.singleton = GlobalInventory(*row)
        else:
            # If no row exists, create a row with default values
            raise Exception("No global inventory row exists")
            # with db.engine.begin() as connection:
            #     sql_to_execute = (
            #         f"INSERT INTO {GlobalInventory.table_name} (created_at, num_red_potions, num_red_ml, gold) "
            #         f"VALUES (0, 0, 0, 0)"
            #     )
            #     connection.execute(sql_to_execute)
            #     GlobalInventory.singleton = GlobalInventory(0, 0, 0, 0)

            #if there is, then set the singleton to that row
            #if there isn't, then create a row with the default values
        return GlobalInventory.singleton


    def get_inventory(self):
        return {
            "number_of_potions": self.num_red_potions,
            "ml_in_barrels": self.num_red_ml,
            "gold": self.gold,
        }

    @staticmethod
    def get_inventory():
        try:
            total_ml = 0
            sql_to_execute = text(f"SELECT num_ml FROM {WholesaleInventory.table_name}")
            with db.engine.begin() as connection:
                result = connection.execute(sql_to_execute)
                rows = result.fetchall()
                #itterat through the rows and add up all their millileters
                for row in rows:
                    total_ml += row[0]
            gold = Transaction.get_current_balance()
            total_potions = RetailInventory.get_total_potions()
            return {
                "number_of_potions": total_potions,
                "ml_in_barrels": total_ml,
                "gold": gold,
            }
        except Exception as error:
            print("unable to get inventory: ", error)
            return "ERROR"
  


    

    def get_catalog(self):

        catalog_array = []
        if(self.num_red_potions > 0):
            catalog_array.append({
                "sku": GlobalInventory.red_potion_sku,
                "name": "red potion",
                "quantity": self.num_red_potions,
                "price": GlobalInventory.price_of_red_potion,
                "potion_type": [100, 0, 0, 0],
            })
        
        return catalog_array
            
    def get_bottler_plan(self):

        quantity_of_red_to_bottle = math.floor(self.num_red_ml/100)
        array_of_potion_types = []
        if(quantity_of_red_to_bottle != 0):
            array_of_potion_types.append(
                {
                "potion_type": [100, 0, 0, 0],
                "quantity": quantity_of_red_to_bottle,
            }
            )

        return array_of_potion_types  


    def get_wholesale_plan(self, wholesale_catalog: list[Barrel]):
        if(len(wholesale_catalog) == 0):
            return []
        
        buy_one_barrel = False
        
        for catalog_item in wholesale_catalog:
            if (catalog_item.sku == GlobalInventory.red_potion_barrel_sku and catalog_item.quantity > 0 and self.gold >= catalog_item.price):
                buy_one_barrel = True
                break

        if(buy_one_barrel):
             return [{
                "sku": GlobalInventory.red_potion_barrel_sku,
                "quantity": 1,
             }]
        else:
            return []

    def accept_potions_delivery(self, potions_delivered: list[PotionInventory]):
        try: 

            for potion in potions_delivered:
                if(potion.potion_type == [100, 0, 0, 0]): #TODO: are the potion types formatted like this or adding up to 100?
                    #update the specific row in the table self.id
                    sql_to_execute = text(f"UPDATE {GlobalInventory.table_name} SET num_red_potions = num_red_potions + :num_delivered, num_red_ml = num_red_ml - used_red_ml WHERE id = :id")
                    with db.engine.begin() as connection:
                        connection.execute(sql_to_execute, {"num_delivered": potion.quantity, "id": self.id, "used_red_ml": potion.quantity*100}) #TODO: make sure this is correct
            return "OK"
        except Exception as error:
            print("unable to accept potion delivery: ", error)
            return "ERROR"

    def accept_barrels_delivery(self, barrels_delivered: list[Barrel]):
        try:
            for barrel in barrels_delivered:
                if(barrel.sku == GlobalInventory.red_potion_barrel_sku):
                    #update the specific row in the table self.id
                    #also decrease gold by the cost of the barrel
                    sql_to_execute = text(f"UPDATE {GlobalInventory.table_name} SET num_red_ml = num_red_ml + :ml_red, gold = gold - :cost_of_barrel WHERE id = :id")
                    with db.engine.begin() as connection:
                        connection.execute(sql_to_execute, {"ml_red": barrel.quantity * barrel.ml_per_barrel, "cost_of_barrel": barrel.quantity*barrel.price, "id": self.id})
            return "OK"
        except Exception as error:
            print("unable to accept barrel delivery: ", error)
            return "ERROR"
            

    def items_available(self, items: dict[str, int]):
        for item_sku, quantity in items.items():
            if item_sku == GlobalInventory.red_potion_sku:
                if quantity > self.num_red_potions:
                    raise Exception("Not enough red potions available")
            else:
                raise Exception("Item not found")
            

    def adjust_inventory(self, items: dict[str, int]):
        #update the specific row in the table self.id

        try:
            total_gold_paid = GlobalInventory.price_of_red_potion*items[GlobalInventory.red_potion_sku]
            sql_to_execute = text(f"UPDATE {GlobalInventory.table_name} SET num_red_potions = num_red_potions - :quantity, gold = gold + :total_gold_paid WHERE id = :id")
            with db.engine.begin() as connection:
                connection.execute(sql_to_execute, {"quantity": items[GlobalInventory.red_potion_sku], "id": self.id, "total_gold_paid": total_gold_paid})
        except: 
            raise Exception("Could not adjust inventory")

        return {"total_potions_bought": items[GlobalInventory.red_potion_sku], "total_gold_paid": total_gold_paid}