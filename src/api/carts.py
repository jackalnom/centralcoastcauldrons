from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from ..models.cart import Cart, NewCart, CartItem, CartCheckout
router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)





@router.post("/")
def create_cart(new_cart: NewCart):
    #return a unique cart id
    """ """

    cart = Cart(new_cart)

    return {"cart_id": cart.id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    #what do we return from this endpoint?? dont need to do this
    """ """

    return {}






@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    #do we just set this to one? or do we set it to the max possible? 
    #when stuff is in the cart is it reserved for them? should it be taken out of the db?
    """ """

    cart = Cart.get_cart(cart_id)
    cart.set_item_quantity(item_sku, cart_item)

    return "OK"




@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #when you checkout 
    cart = Cart.get_cart(cart_id) 
    return cart.checkout(cart_checkout)
