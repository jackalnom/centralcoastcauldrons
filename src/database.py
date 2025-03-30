from src import config
from sqlalchemy import create_engine

connection_url = config.get_settings().POSTGRES_URI
engine = create_engine(connection_url, pool_pre_ping=True)
