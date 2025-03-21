from fastapi import APIRouter
from pydantic import BaseModel, Field, conint, field_validator, ValidationInfo
from typing import List, Annotated

router = APIRouter()

class PotionType(BaseModel):
    r: Annotated[int, Field(ge=0, le=100)]
    g: Annotated[int, Field(ge=0, le=100)]
    b: Annotated[int, Field(ge=0, le=100)]
    d: Annotated[int, Field(ge=0, le=100)]

    @field_validator("d", mode="before")
    @classmethod
    def check_sum(cls, v: int, info: ValidationInfo) -> int:
        values = info.data
        if "r" in values and "g" in values and "b" in values:
            if values["r"] + values["g"] + values["b"] + v != 100:
                raise ValueError("r, g, b, d must add up to 100")
        return v


class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
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
