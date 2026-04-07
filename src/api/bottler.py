from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
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
                    red_ml = red_ml - :red_ml
                    blue_ml = blue_ml - :blue_ml
                    green_ml = green_ml - :green_ml
                    dark_ml = dark_ml - :dark_ml
                    """
                ),
                [{"red_ml": potion.potion_type[0],
                  "blue_ml": potion.potion_type[1],
                  "green_ml": potion.potion_type[2],
                  "dark_ml": potion.potion_type[3]}],
            )
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE global_inventory SET 
                    red_potions = red_potions + :red_potions
                    blue_potions = blue_potions + :blue_potions
                    green_potions = green_potions + :green_potions
                    dark_potions = dark_potions + :dark_potions
                    """
                ),
                [{"red_potions": potion.potion_type[0] * potion.quantity,
                  "blue_potions": potion.potion_type[1] * potion.quantity,
                  "green_potions": potion.potion_type[2] * potion.quantity,
                  "dark_potions": potion.potion_type[3] * potion.quantity}],
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
    # TODO: Create a real bottle plan logic
    return [
        PotionMixes(
            potion_type=[100, 0, 0, 0],
            quantity=5,
        )
    ]


@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """

    # TODO: Fill in values below based on what is in your database
    return create_bottle_plan(
        red_ml=100,
        green_ml=0,
        blue_ml=0,
        dark_ml=0,
        maximum_potion_capacity=50,
        current_potion_inventory=[],
    )


if __name__ == "__main__":
    print(get_bottle_plan())
