
from pydantic import BaseModel

class NewCart(BaseModel):
  customer: str


class Cart:
  id_counter = 0
  virtual_carts_table = {}
  def __init__(self, new_cart: NewCart):
    self.id = Cart.id_counter
    Cart.id_counter += 1
    self.items = {}
    self.customer_id = new_cart.customer
    Cart.virtual_carts_table[self.id] = self



  
