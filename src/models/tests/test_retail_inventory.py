
import logging
from ..retail_inventory import RetailInventory
def testgetinventory():
  inventory = RetailInventory.get_inventory()
  logging.info(f'inventory is {inventory}')
  
