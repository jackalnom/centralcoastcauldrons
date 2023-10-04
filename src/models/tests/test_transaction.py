import logging
from ..transaction import Transaction
def test_get_current_balance():
  current_balance = Transaction.get_current_balance()
  assert current_balance == 0
  
