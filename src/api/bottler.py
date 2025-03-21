from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, conint, validator
from typing import List
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionMixes(BaseModel):
    potion_type: List[conint(ge=0, le=100)]
    quantity: conint(ge=1, le=10000)

    @validator('potion_type')
    def validate_potion_type(cls, potion_type):
        if len(potion_type) != 4:
            raise ValueError('potion_type must have exactly 4 elements: [r, g, b, d]')
        if sum(potion_type) != 100:
            raise ValueError('Sum of potion_type values must be exactly 100')
        return potion_type


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_bottles(potions_delivered: List[PotionMixes], order_id: int):
    """
    Delivery of potions requested after plan. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")
    pass


@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """
    return [
        PotionMixes(
            potion_type=[100, 0, 0, 0],
            quantity=5,
        )
    ]


if __name__ == "__main__":
    print(get_bottle_plan())
