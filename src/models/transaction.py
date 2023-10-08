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
        #FIXME: add a description to the OG transaction
        sql_to_execute = text(f"INSERT INTO {Transaction.table_name} (starting_balance, ending_balance) VALUES (0, 100)")
        result = connection.execute(sql_to_execute)
        current_balance = 100
      else:
        current_balance = row[1]
        print("id", row[0])
    return current_balance


  @staticmethod
  def create(transaction_entity_id: int | None, adjustment: int, description: str ):
    try:
      current_balance = Transaction.get_current_balance()
      print("current balance: ", current_balance )
      new_balance = current_balance + adjustment
      sql_to_execute = text(f"INSERT INTO {Transaction.table_name} (starting_balance, ending_balance, transaction_entity_id, description) VALUES (:starting_balance, :ending_balance, :transaction_entity_id, :description)")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"starting_balance": current_balance, "ending_balance": new_balance, "transaction_entity_id": transaction_entity_id, "description": description})
      return "OK"
    except Exception as error:
      print("unable to create transaction: ", error)
      return "ERROR"
    

  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Transaction.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset retail inventory: ", error)
        return "ERROR"

      

