from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
from src import database as db
import sqlalchemy

router = APIRouter()


class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )


# Placeholder function, you will replace this with a database call
def create_catalog() -> List[CatalogItem]:

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT red_potions, green_potions, blue_potions
                FROM global_inventory
                """
            )
        ).one()
    
    items = []
    if row[0] != 0:
        items.append(CatalogItem(sku='red_potions', name="red potion", quantity=row[0], price=75, potion_type=[100,0,0,0]))

    if row[1] != 0:
        items.append(CatalogItem(sku='green_potions', name="green potion", quantity=row[1], price=75, potion_type=[0,100,0,0]))
    if row[2] != 0:
        items.append(CatalogItem(sku='blue_potions', name="blue potion", quantity=row[2], price=75, potion_type=[0,0,100,0]))
    return items


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return create_catalog()
