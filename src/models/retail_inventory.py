from src import database as db
from sqlalchemy.sql import text
from typing import List
from .wholesale_inventory import WholesaleInventory
import json
from pydantic import BaseModel
from .transaction import Transaction

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


class RetailInventory:
  table_name = "retail_inventory"
  potion_price = 60 
  def __init__(self, id, sku: str, name: str, type, quantity, price):
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
        WholesaleInventory.use_potion_inventory(potion.potion_type, potion.quantity)
      return "OK"
    except Exception as error:
        print("unable to accept potion delivery things may be out of sync due to no roleback: ", error)
        return "ERROR"
  

  @staticmethod
  def items_available(items: dict[str, int]):
    inventory = RetailInventory.get_inventory()

    for item_sku, quantity in items.items():
      print("Inventory:", [item.sku for item in inventory])
      print("Looking for SKU:", item_sku)
      print("Type of SKUs in inventory:", [type(item.sku) for item in inventory])
      print("Type of target SKU:", type(item_sku))


      #get the inventory item with the same sku as the item_sku
      inventory_item = None
      for item in inventory:
        print("item.sku:", item.sku)
        print("item_sku:", item_sku)
        if f'{item.sku.strip()}' == f'{item_sku.strip()}':
          inventory_item = item
          break      
      print ("inventory item: ", inventory_item)
      if( inventory_item is None):
        raise Exception("Item not found")
      if inventory_item.quantity < quantity:
        raise Exception("Not enough items available")
    return True  
  

  #FIXME: hardcoded potion price 
  @staticmethod
  def adjust_inventory(items: dict[str, int]):
        #update the specific row in the table self.id
        try:
          total_gold_paid = 0
          total_potions_bought = 0
          for item_sku, quantity in items.items():
            total_gold_paid += RetailInventory.potion_price*quantity
            total_potions_bought += quantity
            sql_to_execute = text(f"UPDATE {RetailInventory.table_name} SET quantity = quantity - :quantity WHERE sku = :sku")
            with db.engine.begin() as connection:
              connection.execute(sql_to_execute, {"quantity": quantity, "sku": item_sku})
          Transaction.create(None, total_gold_paid, f'payment of {total_gold_paid} for {items} potions') 
        except: 
            raise Exception("Could not adjust inventory")

        return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
        

  







    

  

  



      