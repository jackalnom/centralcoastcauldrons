import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy
from src import database as db

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

def update_gold(amount, description=""):
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result= connection.execute(sqlalchemy.text(
            "INSERT INTO stock_ledger(d_gold, description) \
             VALUES (:d_gold, :description)"),
                [{
                    'd_gold':amount,
                    'description':description
                }]
            )
        
def update_ml(amount, color, description=""):
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result= connection.execute(sqlalchemy.text(
            "INSERT INTO stock_ledger(d_:color, description) \
             VALUES (:amount, :description)"),
                [{
                    'amount':amount,
                    'color':color,
                    'description':description,

                }]
            )

def get_potion_id(sku):
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result= connection.execute(sqlalchemy.text(
            "SELECT id \
            FROM potion_inventory \
            WHERE sku=:sku"),
            [{
                'sku':sku
            }]
        )
        return result.first()[0]

def update_potion(amount, id, description=""):
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result= connection.execute(sqlalchemy.text(
            "INSERT INTO potion_ledger (d_quan, potion_id, description) \
             VALUES (:amount, :id, :description)"),
                [{
                    'amount':amount,
                    'id':id,
                    'description':description,

                }]
            )

def get_gold():
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result = connection.execute(sqlalchemy.text(
            "SELECT SUM(d_gold) as gold \
             FROM stock_ledger"))
    return result.first()[0]

def get_ml(color):
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result = connection.execute(sqlalchemy.text(
            "SELECT SUM(d_:color) as ml \
             FROM stock_ledger"),
             [{
                 'color':color
             }])
    return result.first()[0]

def get_all_ml():
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result = connection.execute(sqlalchemy.text(
            "SELECT SUM(d_red) as red, SUM(d_green) as green, SUM(d_blue) as blue, SUM(d_dark) as dark \
             FROM stock_ledger"))
    return result.first()