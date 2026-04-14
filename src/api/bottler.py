from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src.api.helper import get_global_inventory
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionMixes(BaseModel):
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )
    quantity: int = Field(
        ..., ge=1, le=10000, description="Quantity must be between 1 and 10,000"
    )

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[int]) -> List[int]:
        if sum(potion_type) != 100:
            raise ValueError("Sum of potion_type values must be exactly 100")
        return potion_type


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_bottles(potions_delivered: List[PotionMixes], order_id: int):
    """
    Delivery of potions requested after plan. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    for potion in potions_delivered:
        with db.engine.begin() as connection:
            # Placeholder until multi type potions are created.
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE global_inventory SET 
                    red_ml = red_ml - :red_ml,
                    green_ml = green_ml - :green_ml,
                    blue_ml = blue_ml - :blue_ml
                    """
                ),
                [{"red_ml": potion.potion_type[0] * potion.quantity,
                  "green_ml": potion.potion_type[1] * potion.quantity,
                  "blue_ml": potion.potion_type[2] * potion.quantity
                }],
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE global_inventory SET 
                    red_potions = red_potions + :red_potions,
                    green_potions = green_potions + :green_potions,
                    blue_potions = blue_potions + :blue_potions
                    """
                ),
                [{"red_potions": potion.quantity * (potion.potion_type[0] != 0),
                  "green_potions": potion.quantity * (potion.potion_type[1] != 0),
                  "blue_potions": potion.quantity * (potion.potion_type[2] != 0)}],
            )
    pass


def create_bottle_plan(
    red_ml: int,
    green_ml: int,
    blue_ml: int,
    dark_ml: int,
    maximum_potion_capacity: int,
    current_potion_inventory: List[PotionMixes],
) -> List[PotionMixes]:
    mixes = []
    remaining_slots = maximum_potion_capacity
    remaining_slots -= sum([potion.quantity for potion in current_potion_inventory])
    if red_ml >= 100:
        potion_cap = min(remaining_slots, red_ml // 100)
        remaining_slots -= potion_cap
        mixes.append(PotionMixes(potion_type=[100, 0, 0, 0], quantity=potion_cap))
    if green_ml >= 100:
        potion_cap = min(remaining_slots, green_ml // 100)
        remaining_slots -= potion_cap
        mixes.append(PotionMixes(potion_type=[0, 100, 0, 0], quantity=potion_cap))
    if blue_ml >= 100:
        potion_cap = min(remaining_slots, blue_ml // 100)
        remaining_slots -= potion_cap
        mixes.append(PotionMixes(potion_type=[0, 0, 100, 0], quantity=potion_cap))
    return mixes


@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """

    row = get_global_inventory()
    mixes = []
    if row.red_potions > 0:
        mixes.append(PotionMixes(potion_type=[100, 0, 0, 0], quantity=row.red_potions))
    if row.green_potions > 0:
        mixes.append(PotionMixes(potion_type=[0, 100, 0, 0], quantity=row.green_potions))
    if row.blue_potions > 0:
        mixes.append(PotionMixes(potion_type=[0, 0, 100, 0], quantity=row.blue_potions))

    return create_bottle_plan(
        red_ml=row.red_ml,
        green_ml=row.green_ml,
        blue_ml=row.blue_ml,
        dark_ml=0,
        maximum_potion_capacity=50,
        current_potion_inventory=mixes,
    )


if __name__ == "__main__":
    print(get_bottle_plan())
