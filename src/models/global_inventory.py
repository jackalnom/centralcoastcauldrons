#This class should represent the global inventory of the game
import sqlalchemy
from src import database as db
from pydantic import BaseModel
from sqlalchemy.sql import text



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
#columns of created_at, num_red_potions, num_red_ml, gold
    table_name = "global_inventory"
    singleton = None
    def __init__(self, id, created_at, num_red_potions, num_red_ml, gold):
        self.id = id
        self.created_at = created_at
        self.num_red_potions = num_red_potions
        self.num_red_ml = num_red_ml
        self.gold = gold

    
    @staticmethod
    def get_singleton():
        if GlobalInventory.singleton is None:

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

        return GlobalInventory.singleton
            #if there is, then set the singleton to that row
            #if there isn't, then create a row with the default values

    def get_catalog(self):
        if(self.num_red_potions == 0):
            return []
        
        return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": self.num_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
    def get_bottler_plan(self):

        quantity_of_red_to_bottle = self.num_red_ml%100 
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
            if (catalog_item.sku == "SMALL_RED_BARREL" and catalog_item.quantity > 0 and self.gold >= catalog_item.price):
                buy_one_barrel = True
                break

        if(buy_one_barrel):
             return [{
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
             }]
        else:
            return []

    def accept_delivery(self, potions_delivered: list[PotionInventory]):
        for potion in potions_delivered:
            if(potion.potion_type == [100, 0, 0, 0]):
                #update the specific row in the table self.id
                sql_to_execute = text(f"UPDATE {GlobalInventory.table_name} SET num_red_potions = num_red_potions + :quantity WHERE id = :id")
                with db.engine.begin() as connection:
                    connection.execute(sql_to_execute, {"quantity": potion.quantity})

        return "OK"


