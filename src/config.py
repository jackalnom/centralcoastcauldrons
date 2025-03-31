from dotenv import load_dotenv, find_dotenv
import os
from functools import lru_cache

# Load default first
load_dotenv(dotenv_path="default.env", override=False)

# Then override with .env if available
load_dotenv(dotenv_path=find_dotenv(".env"), override=True)


class Settings:
    API_KEY: str | None = os.getenv("API_KEY")
    POSTGRES_URI: str | None = os.getenv("POSTGRES_URI")

    def __init__(self):
        if not self.API_KEY:
            raise ValueError("API_KEY is missing in the environment variables.")
        if not self.POSTGRES_URI:
            raise ValueError("POSTGRES_URI is missing in the environment variables.")


@lru_cache()
def get_settings():
    return Settings()
