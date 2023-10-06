from .global_inventory import Barrel, GlobalInventory
from .transaction import Transaction
from .retail_inventory import RetailInventory
from sqlalchemy.sql import text
from src import database as db


class WholesaleInventory:
  #TODO: update this template code
  table_name = "wholesale_inventory"
  def __init__(self, id, sku, type, num_ml):
    self.id = id
    self.sku = sku
    self.type = type
    self.num_ml = num_ml

  
    
  @staticmethod
  def get_wholesale_plan(wholesale_catalog: list[Barrel]):
    #TODO: update this to the following strategy:
    # 1. If there is a barel type that i don't have at least 50ml, and i have enough gold to buy it, then buy it.
    
    if(len(wholesale_catalog) == 0):
        return []
        
    buy_one_barrel = False
    
    for catalog_item in wholesale_catalog:
        if (catalog_item.sku == GlobalInventory.red_potion_barrel_sku and catalog_item.quantity > 0 and Transaction.get_current_balance() >= catalog_item.price):
            buy_one_barrel = True
            break

    if(buy_one_barrel):
          return [{
            "sku": GlobalInventory.red_potion_barrel_sku,
            "quantity": 1,
          }]
    else:
        return []


  @staticmethod
  def accept_barrels_delivery (barrels_delivered: list[Barrel]):
    try:
      for barrel in barrels_delivered:
        #TODO: Implement rollback so it cant just do one of the following
        WholesaleInventory.add_to_inventory(barrel)
        Transaction.create(None, barrel.price * barrel.quantity * -1, f'payment for delivery of {barrel.quantity} {barrel.sku} barrels of type {barrel.potion_type}') #flush this out
  
      return "OK"
    except Exception as error:
        print("unable to accept barrel delivery things may be out of sync due to no roleback: ", error)
        return "ERROR"
    
  def add_to_inventory(barrel: Barrel):
    try:
      barrel = None
      sql_to_execute = text(f"SELECT * FROM {WholesaleInventory.table_name} WHERE sku = :sku")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"sku": barrel.sku}).fetchone()
        if(result == None):
          sql_to_execute = text(f"INSERT INTO {WholesaleInventory.table_name} SET sku = :sku, type = :type, num_ml = :num_ml")
          connection.execute(sql_to_execute, {"sku": barrel.sku, "type": barrel.potion_type, "num_ml": barrel.quantity * barrel.ml_per_barrel})
        else:
          sql_to_execute = text(f"UPDATE {WholesaleInventory.table_name} SET num_ml = num_ml + :num_ml WHERE sku = :sku")
          connection.execute(sql_to_execute, {"sku": barrel.sku, "num_ml": barrel.quantity * barrel.ml_per_barrel})
      return 'OK'
    except Exception as error:
        print("unable to add to inventory: ", error)
        return "ERROR"
    
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
  


    
   
  
