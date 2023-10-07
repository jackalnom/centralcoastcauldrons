
from pydantic import BaseModel
from .global_inventory import GlobalInventory
from sqlalchemy.sql import text
from src import database as db


class NewCart(BaseModel):
  customer: str

class CartItem(BaseModel):
  quantity: int


class CartCheckout(BaseModel):
    payment: str

class InventoryItem(BaseModel):
  sku: str
  quantity: int


#TODO: update this class to have some functionality
class Cart:
  
  table_name = "cart"
  def __init__(self, id, customer_id):
    self.id = id 
    self.customer_id = customer_id
    
  def get_cart(cart_id: int) -> 'Cart':
    #try to find the cart in the cart table and return it
    raise Exception("Not Implemented")



  def set_item_quantity(self, item_sku: str, cart_item: CartItem): 
    self.items[item_sku] = cart_item.quantity

  def checkout(self, cart_checkout: CartCheckout):
    #TODO: check if the payment string is valid
    checkout_result = {}
    if self.items.items() == {}:
      raise Exception("Transation Failed: Cart is empty")
    try:
      GlobalInventory.get_singleton().items_available(self.items)
    except:
      raise Exception("Transaction Failed: Not enough items available")
    try: 
      checkout_result = GlobalInventory.get_singleton().adjust_inventory(self.items)
    except:
      raise Exception("Transaction Failed: Could not adjust inventory")

    #get rid of cart
    self.items = {}
    Cart.virtual_carts_table.pop(self.id)

    return checkout_result

  @staticmethod
  def delete_all_carts():
    Cart.virtual_carts_table = {}


  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Cart.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset retail inventory: ", error)
        return "ERROR"
  








  
