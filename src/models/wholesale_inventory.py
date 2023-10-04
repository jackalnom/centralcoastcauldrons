from .global_inventory import Barrel, GlobalInventory


class WholesaleInventory:
  #TODO: update this template code
  def __init__(self, id, sku, name, type, num_ml):
    self.id = id
    self.sku = sku
    self.type = type
    self.name = name
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
    


    
   
  
