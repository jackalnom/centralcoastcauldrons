from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)


class Timestamp(BaseModel):
    day: str
    hour: int


@router.post("/current_time", status_code=status.HTTP_204_NO_CONTENT)
def post_time(timestamp: Timestamp):
    """
    Shares what the latest time (in game time) is.
    """
    # TODO: Record day and time of the current tick to associate with later calls
    pass
