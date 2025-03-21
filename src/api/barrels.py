from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, conint, confloat, validator
from typing import List
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: conint(gt=0)
    potion_type: List[confloat(ge=0, le=1)]
    price: conint(ge=0)
    quantity: conint(ge=0)

    @validator('potion_type')
    def validate_potion_type(cls, potion_type):
        if len(potion_type) != 4:
            raise ValueError('potion_type must have exactly 4 elements: [r, g, b, d]')
        if not abs(sum(potion_type) - 1.0) < 1e-6:
            raise ValueError('Sum of potion_type values must be exactly 1')
        return potion_type


class BarrelOrder(BaseModel):
    sku: str
    quantity: conint(gt=0)


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_barrels(barrels_delivered: List[Barrel], order_id: int):
    """
    Processes barrels delivered based on the provided order_id. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    pass


@router.post("/plan", response_model=List[BarrelOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Barrel]):
    """
    Gets the plan for purchasing wholesale barrels. The call passes in a catalog of available barrels
    and the shop returns back which barrels they'd like to purchase and how many.
    """
    print(f"barrel catalog: {wholesale_catalog}")
    return [
        BarrelOrder(sku="SMALL_RED_BARREL", quantity=1)
    ]