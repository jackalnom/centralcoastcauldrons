import sqlalchemy
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    sql_to_execute1 = sqlalchemy.text("insert into global_carts (customer_name) values ('{0}')".format(new_cart.customer))
    sql_to_execute2 = sqlalchemy.text("select max(cart_id) from global_carts")
    with db.engine.begin() as connection:
        connection.execute(sql_to_execute1)
        result = connection.execute(sql_to_execute2).one()
    return {"cart_id": result[0]}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    sql_to_execute = sqlalchemy.text("select * from global_carts where cart_id = {}".format(cart_id))
    with db.engine.begin() as connection:
        try:
            result = connection.execute(sql_to_execute).one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="Item not found")

    return {"customer": result[1]}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    return {"total_potions_bought": 1, "total_gold_paid": 50}
