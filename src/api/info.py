from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    day: str
    hour: int

@router.post("/current_time")
def post_time(timestamp: Timestamp):
    """
    Share current time.
    """
    sql_to_execute = f"UPDATE global_time SET day = '{timestamp.day}', hour = {timestamp.hour}"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

