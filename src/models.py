import sqlalchemy
from src import database

# SQL table for Potions
meta_potions = sqlalchemy.MetaData()
potions_table = sqlalchemy.Table("potions", meta_potions, autoload_with=database.engine)

# SQL table for Customer
meta_customer = sqlalchemy.MetaData()
customer_table = sqlalchemy.Table("customers", meta_customer, autoload_with=database.engine)


# SQL table for Cart
meta_cart = sqlalchemy.MetaData()
carts_table = sqlalchemy.Table("carts", meta_cart, autoload_with=database.engine)

# SQL table for Global
meta_global = sqlalchemy.MetaData()
global_table = sqlalchemy.Table("global_inventory_temp", meta_global, autoload_with=database.engine)