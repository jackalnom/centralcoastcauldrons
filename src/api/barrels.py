from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db
import random

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int = Field(gt=0, description="Must be greater than 0")
    potion_type: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d] that sum to 1.0",
    )
    price: int = Field(ge=0, description="Price must be non-negative")
    quantity: int = Field(ge=0, description="Quantity must be non-negative")

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[float]) -> List[float]:
        if len(potion_type) != 4:
            raise ValueError("potion_type must have exactly 4 elements: [r, g, b, d]")
        if not abs(sum(potion_type) - 1.0) < 1e-6:
            raise ValueError("Sum of potion_type values must be exactly 1.0")
        return potion_type


class BarrelOrder(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


@dataclass
class BarrelSummary:
    gold_paid: int


def calculate_barrel_summary(barrels: List[Barrel]) -> BarrelSummary:
    return BarrelSummary(gold_paid=sum(b.price * b.quantity for b in barrels))


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_barrels(barrels_delivered: List[Barrel], order_id: int):
    """
    Processes barrels delivered based on the provided order_id. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    ml_options = ("red_ml", "green_ml", "blue_ml")

    delivery = calculate_barrel_summary(barrels_delivered)
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                f"""
                UPDATE global_inventory 
                SET gold = gold - :gold_paid
                """
            ),
            [{"gold_paid": delivery.gold_paid}]
        )


    for barrel in barrels_delivered:
        ml =  barrel.ml_per_barrel * barrel.quantity

        highest_type = max(barrel.potion_type)
        select = barrel.potion_type.index(highest_type)

        mlType = ml_options[select]
        # Remove gold and add potion quantity
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    f"""
                    UPDATE global_inventory 
                    SET {mlType} = {mlType} + :ml
                    """
                ),
                [{"ml": ml}]
            )

    pass


def create_barrel_plan(
    gold: int,
    max_barrel_capacity: int,
    current_red_ml: int,
    current_green_ml: int,
    current_blue_ml: int,
    current_dark_ml: int,
    wholesale_catalog: List[Barrel],
) -> List[BarrelOrder]:
    print(
        f"gold: {gold}, max_barrel_capacity: {max_barrel_capacity}, current_red_ml: {current_red_ml}, current_green_ml: {current_green_ml}, current_blue_ml: {current_blue_ml}, current_dark_ml: {current_dark_ml}, wholesale_catalog: {wholesale_catalog}"
    )

    # Select random potion color (RGB)
    potion_select = random.randrange(3)
    potion_options = ("red_potions", "green_potions", "blue_potions")

    # find find cheapest barrel
    barrel = min(
        (barrel for barrel in wholesale_catalog if barrel.potion_type[potion_select] == 1),
        key=lambda b: b.price,
        default=None,
    )

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT {potion_options[potion_select]}
                FROM global_inventory
                """
            )
        ).one()

    # make sure we can afford it and need potions
    if barrel and barrel.price <= gold and row[0] < 5:
        return [BarrelOrder(sku=barrel.sku, quantity=1)]

    # return an empty list if no affordable red barrel is found
    return []


@router.post("/plan", response_model=List[BarrelOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Barrel]):
    """
    Gets the plan for purchasing wholesale barrels. The call passes in a catalog of available barrels
    and the shop returns back which barrels they'd like to purchase and how many.
    """
    print(f"barrel catalog: {wholesale_catalog}")

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT gold, red_ml, green_ml, blue_ml
                FROM global_inventory
                """
            )
        ).one()

        gold = row[0]
        red_ml = row[1]
        green_ml = row[2]
        blue_ml = row[3]

    return create_barrel_plan(
        gold=gold,
        max_barrel_capacity=10000,
        current_red_ml=red_ml,
        current_green_ml=green_ml,
        current_blue_ml=blue_ml,
        current_dark_ml=0,
        wholesale_catalog=wholesale_catalog,
    )
