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
             VALUES (:d_gold, ':description')"),
                [
                    {'d_gold':amount},
                    {'description':description}
                ]
            )

def get_gold():
    with db.engine.begin() as connection:
        # check if sku exists in table already
        result = connection.execute(sqlalchemy.text(
            "SELECT SUM(d_gold) as gold \
             FROM stock_ledger"))
    return result.first()[0]