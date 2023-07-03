from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    return [
            {
                "sku": "RED_POTION",
                "name": "red potion",
                "quantity": 1,
                "price": 3,
                "potion_type": [100, 0, 0, 0],
            }
        ]
