from fastapi import APIRouter
from pydantic import BaseModel, Field, conint, constr, validator
from typing import List, Literal

router = APIRouter()

class PotionType(BaseModel):
    r: conint(ge=0, le=100)
    g: conint(ge=0, le=100)
    b: conint(ge=0, le=100)
    d: conint(ge=0, le=100)

    @validator('d')
    def check_sum(cls, v, values):
        if 'r' in values and 'g' in values and 'b' in values:
            if values['r'] + values['g'] + values['b'] + v != 100:
                raise ValueError('r, g, b, d must add up to 100')
        return v


class CatalogItem(BaseModel):
    sku: constr(regex=r'^[a-zA-Z0-9_]{1,20}$')
    name: str
    quantity: conint(ge=1, le=10000)
    price: conint(ge=1, le=500)
    potion_type: PotionType

# Placeholder function, you will replace this with a database call
def get_sample_items() -> List[CatalogItem]:
    return [
        CatalogItem(
            sku="RED_POTION_0",
            name="red potion",
            quantity=1,
            price=50,
            potion_type=PotionType(r=100, g=0, b=0, d=0)
        )
    ]


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return get_sample_items()