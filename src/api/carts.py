from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(request: Request, new_cart: NewCart):
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

class CartCheckout(BaseModel):
    payment: str
    gold_paid: int

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    return {"order_id": 1}

class CartPickupItem(BaseModel):
    potion_type: str
    quantity: int

class CartPickup(BaseModel):
    # Description of items
    items: list[CartPickupItem]

@router.post("/{cart_id}/pickup")
def pickup_order(cart_id: int, cart_pickup: CartPickup):
    """ """

    return {"order_id": 1}

class CartRefund(BaseModel):
    gold_refunded: int

@router.post("/{cart_id}/refund")
def refund_order(cart_id: int, cart_refund: CartRefund):
    """ """

    return {"order_id": 1}