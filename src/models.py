import sqlalchemy
from src import database

# SQL table for Potions
meta_potions = sqlalchemy.MetaData()
potions_table = sqlalchemy.Table("potions", meta_potions, autoload_with=database.engine)

# SQL table for Potions Ledger
meta_potions_ledger = sqlalchemy.MetaData()
potions_ledger_table = sqlalchemy.Table("potion_ledger", meta_potions_ledger, autoload_with=database.engine)

# SQL table for Customer
meta_customer = sqlalchemy.MetaData()
customer_table = sqlalchemy.Table("customers", meta_customer, autoload_with=database.engine)


# SQL table for Cart
meta_cart = sqlalchemy.MetaData()
carts_table = sqlalchemy.Table("carts", meta_cart, autoload_with=database.engine)

# SQL table for inventory ledger
meta_inventory_ledger = sqlalchemy.MetaData()
inventory_ledger_table = sqlalchemy.Table("inventory_ledger", meta_inventory_ledger, autoload_with=database.engine)