
from pydantic import BaseModel
from .global_inventory import GlobalInventory
from .retail_inventory import RetailInventory

class NewCart(BaseModel):
  customer: str

class CartItem(BaseModel):
  quantity: int


class CartCheckout(BaseModel):
  payment: str

class InventoryItem(BaseModel):
  sku: str
  quantity: int


class Cart:
  id_counter = 0
  virtual_carts_table = {}
  def __init__(self, new_cart: NewCart):
    self.id = Cart.id_counter
    Cart.id_counter += 1
    self.items = {}
    self.customer_id = new_cart.customer
    Cart.virtual_carts_table[self.id] = self


  def get_cart(cart_id: int):
    if cart_id not in Cart.virtual_carts_table:
      raise Exception("Cart not found")
    return Cart.virtual_carts_table[cart_id]

  def set_item_quantity(self, item_sku: str, quantity: int):
    self.items[item_sku] = quantity

class Cart:
  id_counter = 0
  virtual_carts_table = {}
  def __init__(self, new_cart: NewCart):
    self.id = Cart.id_counter
    Cart.id_counter += 1
    self.items = {}
    self.customer_id = new_cart.customer
    Cart.virtual_carts_table[self.id] = self


  def get_cart(cart_id: int) -> 'Cart':
    if cart_id not in Cart.virtual_carts_table:
      raise Exception("Cart not found")
    return Cart.virtual_carts_table[cart_id]

  def set_item_quantity(self, item_sku: str, cart_item: CartItem): 
    self.items[item_sku] = cart_item.quantity

  def checkout(self, cart_checkout: CartCheckout):
    #TODO: check if the payment string is valid
    checkout_result = {}
    if self.items.items() == {}:
      raise Exception("Transation Failed: Cart is empty")
    try:
      RetailInventory.items_available(self.items)
    except Exception as error:
      raise Exception("Transaction Failed: Not enough items available", error)
    try: 
      checkout_result = RetailInventory.adjust_inventory(self.items)
    except Exception as error:
      raise Exception("Transaction Failed: Could not adjust inventory", error)

    #get rid of cart
    self.items = {}
    Cart.virtual_carts_table.pop(self.id)

    return checkout_result

  @staticmethod
  def delete_all_carts():
    Cart.virtual_carts_table = {}
  






  





  
