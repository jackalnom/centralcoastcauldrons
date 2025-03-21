from fastapi import APIRouter
from pydantic import BaseModel, Field, conint, field_validator, ValidationInfo
from typing import List, Annotated

router = APIRouter()

class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
    potion_type: List[int] = Field(..., min_items=4, max_items=4, description="Must contain exactly 4 elements: [r, g, b, d]")


# Placeholder function, you will replace this with a database call
def get_sample_items() -> List[CatalogItem]:
    return [
        CatalogItem(
            sku="RED_POTION_0",
            name="red potion",
            quantity=1,
            price=50,
            potion_type=[100, 0, 0, 0]
        )
    ]


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return get_sample_items()
