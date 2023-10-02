import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src import database as db
from src.api import auth

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
    print("calling create_cart with new_cart:", new_cart)
    create_cart_sql = sqlalchemy.text(
        "insert into global_carts (customer_name) values ('{0}')".format(new_cart.customer))
    print("create_cart_sql:", create_cart_sql)
    get_cart_id_sql = sqlalchemy.text("select max(cart_id) from global_carts")
    print("get_cart_id_sql:", get_cart_id_sql)
    with db.engine.begin() as connection:
        connection.execute(create_cart_sql)
        print("Executed create_cart_sql")
        result = connection.execute(get_cart_id_sql).one()
        print("Executed get_cart_id_sql")
    payload = {"cart_id": result[0]}
    print(payload)

    return payload


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    print("calling get_cart with cart_id:", cart_id)
    get_cart_sql = sqlalchemy.text("select * from global_carts where cart_id = {}".format(cart_id))
    print("get_cart_sql:", get_cart_sql)
    with db.engine.begin() as connection:
        try:
            result = connection.execute(get_cart_sql).one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="Item not found")
    payload = {"customer": result[1]}
    print(payload)

    return payload


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("Calling set_item_quantity:", "cart_id:", cart_id, "item_sku:", item_sku, "cart_item:", cart_item)
    set_item_sql = sqlalchemy.text(
        "update global_carts set num_red_potions = {0}, total_price = 50 where cart_id = {1}".format(cart_item.quantity, cart_id))
    print("sql_item_sql:", set_item_sql)
    with db.engine.begin() as connection:
        connection.execute(set_item_sql)
    return "OK"


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("Calling checkout:", "cart_id:", cart_id, "cart_checkout:", cart_checkout)
    get_cart_sql = sqlalchemy.text("select * from global_carts where cart_id = {}".format(cart_id))
    print("get_cart_sql:", get_cart_sql)
    reset_cart_sql = sqlalchemy.text(
        "update global_carts set num_red_potions = 0, total_price = 0 where cart_id = {0}".format(cart_id))
    print("reset_cart_sql:", reset_cart_sql)
    with db.engine.begin() as connection:
        result = connection.execute(get_cart_sql).one()
        print("Executed get_cart_sql")
        print("get_cart result:", result)
        update_inventory_sql = sqlalchemy.text(
            "update global_inventory set num_red_potions = num_red_potions - {0}, gold = gold + {1}"
            .format(result[2], result[3]))
        print("update_inventory_sql:", update_inventory_sql)
        connection.execute(reset_cart_sql)
        print("Executed reset_cart_sql")
        connection.execute(update_inventory_sql)
        print("Executed update_inventory_sql")

    return {"total_potions_bought": 1, "total_gold_paid": 50}
