from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    return {
        "items": [
            {
                "sku": "blah",
                "name": "item1",
                "quantity": 5,
                "price": 1.00,
                "description": "item1 description",
            }
        ]
    }
