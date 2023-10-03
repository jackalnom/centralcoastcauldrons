class Transaction: 

  #TODO: update template code
  def __init__(self, cart: Cart, cart_checkout: CartCheckout):
    self.cart = cart
    self.cart_checkout = cart_checkout
    self.inventory = GlobalInventory.get_singleton()
    self.customer = Customer.get_customer(cart.customer_id)
    self.items = self.cart.items
    self.total = 0
    self.payment = cart_checkout.payment
    self.transaction_id = Transaction.id_counter
    Transaction.id_counter += 1
    self.customer.add_transaction(self)