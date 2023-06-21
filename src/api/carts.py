from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/")
def create_cart(request: Request):
    """ """
    if request.state.is_demo:
        return {"cart_id": 1, "is_demo": True}

    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {}


class CartItem(BaseModel):
    quantity: int


@router.put("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    # Handle case with invalid sku

    # Handle invalid quantity of sku

    return {"cart_id": 1}


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """

    return {"order_id": 1}
