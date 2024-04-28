import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv(override=True)
    
    if (os.environ.get("DEV_MODE") == 'true'):
        print('dev mode')
        return os.environ.get("DEV_POSTGRES_URI")
    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)