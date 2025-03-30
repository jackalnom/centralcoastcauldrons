from dotenv import load_dotenv, find_dotenv
import os
from functools import lru_cache

# Load default first
load_dotenv(dotenv_path="default.env", override=False)

# Then override with .env if available
load_dotenv(dotenv_path=find_dotenv(".env"), override=True)


class Settings:
    API_KEY: str = os.getenv("API_KEY")
    POSTGRES_URI: str = os.getenv("POSTGRES_URI")


@lru_cache()
def get_settings():
    return Settings()
