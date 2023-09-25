#This class should represent the global inventory of the game
import sqlalchemy
from src import database as db


class GlobalInventory:
#columns of created_at, num_red_potions, num_red_ml, gold
    table_name = "global_inventory"
    singleton = None
    def __init__(self, created_at, num_red_potions, num_red_ml, gold):
        self.created_at = created_at
        self.num_red_potions = num_red_potions
        self.num_red_ml = num_red_ml
        self.gold = gold

    
    @staticmethod
    def get_singleton():
        if GlobalInventory.singleton is None:

            #check to see if there is a row in the table

            sql_to_execute = f"SELECT * FROM {GlobalInventory.table_name} LIMIT 1"

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
    



