import os
import dotenv
from sqlalchemy import create_engine, text


def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("CONNECTION_URI")


engine = create_engine(database_connection_url(), pool_pre_ping=True)


def get_global_inventory():
    with engine.begin() as connection:
        select_statement = text(
            "SELECT num_red_potions, num_red_ml, gold from global_inventory"
        )
        current_inventory = connection.execute(select_statement)
        current_inventory = current_inventory.first()._asdict()
        return current_inventory


def execute(command):
    with engine.begin() as connection:
        connection.execute(text(command))
