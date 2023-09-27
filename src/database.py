import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)


# try:
#     # Connect to the database
#     with engine.connect() as connection:
#         # Execute a simple query
#         result = connection.execute("SELECT 1")
#         print("Database connection successful:", result.fetchone())
# except Exception as e:
#     print("Database connection failed:", e)