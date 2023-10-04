from sqlalchemy import text
from src import database as db
class Transaction: 
  table_name = "transaction"

  #TODO: update template code
  def __init__(self, id, starting_balance, ending_balance, transaction_entity_id, created_at):
    self.id = id
    self.endin_balance = ending_balance
    self.starting_balance = starting_balance
    self.transaction_entity_id = transaction_entity_id
    self.created_at = created_at

  @staticmethod
  def get_current_balance():
    current_balance = 0
    #get the most recent transaction and extract the ending balance, if there are no transactions then create the first transaction that is zeroed out
    sql_to_execute = text(f"SELECT id, ending_balance FROM {Transaction.table_name} ORDER BY created_at DESC LIMIT 1")
    with db.engine.begin() as connection:
      result = connection.execute(sql_to_execute)
      row = result.fetchone()
      if row is None:
        sql_to_execute = text(f"INSERT INTO {Transaction.table_name} (starting_balance, ending_balance) VALUES (0, 0)")
        result = connection.execute(sql_to_execute)
        current_balance = 0
      else:
        current_balance = row[1]
    return current_balance
    