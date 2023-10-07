from .global_inventory import Barrel, GlobalInventory
from .transaction import Transaction
from .retail_inventory import RetailInventory
from sqlalchemy.sql import text
from src import database as db
import math
from threading import Lock
from timeout_decorator import timeout

lock = Lock()

class WholesaleInventory:
  #TODO: update this template code
  table_name = "wholesale_inventory"
  def __init__(self, id, sku, type, num_ml):
    self.id = id
    self.sku = sku
    self.type = type
    self.num_ml = num_ml

  @staticmethod
  def get_bottler_plan():
    try:
      sql_to_execute = text(f"SELECT id, sku, type, num_ml FROM {WholesaleInventory.table_name}")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        bottler_plan = []
        for row in rows:
          if(row[3] >= 100):
            max_potions = math.floor(row[3] / 100)
            adjusted_potion_type = [x*100 for x in row[2]]
            bottler_plan.append({
             "potion_type": adjusted_potion_type,
             "quantity": max_potions 
            }) 
        return bottler_plan
    except Exception as error:
        print("unable to get bottler plan: ", error)
        return "ERROR"

  @staticmethod
  def get_wholesale_plan(wholesale_catalog: list[Barrel]):
    #TODO: update this to the following strategy:
    # 1. If there is a barel type that i don't have at least 50ml, and i have enough gold to buy it, then buy it.
    wholesale_plan = []
    available_balance = Transaction.get_current_balance()
    current_wholesale_materials = {}
    for catalog_item in wholesale_catalog:
      hashable_potion_type = ",".join(map(str, catalog_item.potion_type))
      potion_stock = WholesaleInventory.get_stock(catalog_item.potion_type)
      current_wholesale_materials[hashable_potion_type] = potion_stock
      if (current_wholesale_materials[hashable_potion_type] < 100 and catalog_item.price <= available_balance ):
        available_balance -= catalog_item.price
        current_wholesale_materials[hashable_potion_type] = catalog_item.ml_per_barrel
        wholesale_plan.append({
          "sku": catalog_item.sku,
          "quantity": 1
        })
    return wholesale_plan

  @staticmethod
  def get_stock(potion_type: list[int]):
    try:
      sql_to_execute = text(f"SELECT num_ml FROM {WholesaleInventory.table_name} WHERE type = :type")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"type": potion_type})
        rows = result.fetchall()
        total_ml = 0
        for row in rows:
          total_ml += row[0]
        return total_ml
    except Exception as error:
        print("unable to get potion stock: ", error)
        return "ERROR"
    
  @staticmethod
  def accept_barrels_delivery (barrels_delivered: list[Barrel]):
    try:
      with lock:
        for barrel in barrels_delivered:
          if (barrel.price * barrel.quantity > Transaction.get_current_balance()):
              print("not enough gold to pay for delivery")
              return "ERROR"
          response = WholesaleInventory.add_to_inventory(barrel)
          if (response == "ERROR"):
            return "ERROR"
          delta = barrel.quantity * barrel.price * -1
          Transaction.create(None, delta, f'payment of {delta} for delivery of {barrel.quantity} {barrel.sku} barrels of type {barrel.potion_type}') #flush this out

      return "OK"
    except Exception as error:
        print("unable to accept barrel delivery things may be out of sync due to no roleback: ", error)
        return "ERROR"
    
  def add_to_inventory(barrel: Barrel):
    #FIXME: figure out how the fuck to do error handling in python, this thing swallows hella errors
    #FIXME: sku means nothing here, its really most recent sku, should prob be generating sku from type
    try:
      sql_to_execute = text(f"SELECT * FROM {WholesaleInventory.table_name} WHERE sku = :sku")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"sku": barrel.sku}).fetchone()
        if(result == None):
          sql_to_execute = text(f"INSERT INTO {WholesaleInventory.table_name} (sku, type, num_ml) VALUES (:sku, :type, :num_ml)")
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
  
  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {WholesaleInventory.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset wholesale inventory: ", error)
        return "ERROR"
  


    
   
  
