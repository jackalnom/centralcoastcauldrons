from src import database as db
from sqlalchemy.sql import text
from typing import List
from .global_inventory import PotionInventory
import json


class RetailInventory:
  table_name = "retail_inventory"
  potion_price = 60 
  def __init__(self, id, sku, name, type, quantity, price):
    self.id = id
    self.sku = sku
    self.type = type
    self.quantity = quantity
    self.price = price
    self.name = name


  @staticmethod
  def get_inventory():
    #get all the rows from the catalog table and return them as an array of objects
    sql_to_execute = text(f"SELECT id, sku, name, type, quantity, price FROM retail_inventory")

    inventory: List[RetailInventory]= []
    with db.engine.begin() as connection:
      result = connection.execute(sql_to_execute)
      rows = result.fetchall()
      for row in rows:
        inventory.append(RetailInventory(row[0], row[1], row[2], row[3], row[4], row[5]))
    print("inventory: ", inventory)
    return inventory


  @staticmethod
  def get_total_potions():
    try:
      inventory = RetailInventory.get_inventory()
      total_potions = 0
      for item in inventory:
        total_potions += item.quantity
      return total_potions
    except Exception as error:
      print("unable to get total potions: ", error)
      return "ERROR"

  def convert_to_catalog_item(self):
    return {
      "sku": self.sku,
      "name": self.name,
      "quantity": self.quantity,
      "price": self.price,
      "potion_type": self.type
    }
  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {RetailInventory.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset retail inventory: ", error)
        return "ERROR"
  
  
  @staticmethod
  def accept_potions_delivery(potions_delivered: list[PotionInventory]):
    try:
      #check to see if there already exists an entry in the retailinventory with the same type as the potion delivered, if so then update the quantity, if not then create a new entry
      for potion in potions_delivered:
        sql_to_execute = text(f"SELECT id, sku, name, type, quantity, price FROM {RetailInventory.table_name} WHERE type = :type")
        with db.engine.begin() as connection:
          result = connection.execute(sql_to_execute, {"type": json.dumps(potion.potion_type)})
          row = result.fetchone()
          if row is None:
            potion_sku = ",".join(str(x) for x in potion.potion_type)
            sql_to_execute = text(f"INSERT INTO {RetailInventory.table_name} (sku, name, type, quantity, price) VALUES (:sku, :name, :type, :quantity, :price)")
            with db.engine.begin() as connection:
              connection.execute(sql_to_execute, {"sku": potion_sku, "name": potion_sku, "type": json.dumps(potion.potion_type), "quantity": potion.quantity, "price": RetailInventory.potion_price})
          else:
            sql_to_execute = text(f"UPDATE {RetailInventory.table_name} SET quantity = quantity + :quantity WHERE type = :type")
            with db.engine.begin() as connection:
              connection.execute(sql_to_execute, {"quantity": potion.quantity, "type": json.dumps(potion.potion_type)})
      return "OK"
    except Exception as error:
        print("unable to accept potion delivery things may be out of sync due to no roleback: ", error)
        return "ERROR"




    

  

  



      