from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
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
  with db.engine.begin() as connection:
    cart_id = connection.execute(sqlalchemy.text("""
        INSERT INTO carts (customer)
        VALUES (:customer)
        RETURNING cart_id
        """), {"customer": new_cart.customer}).first().cart_id
  return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
  """ """
  with db.engine.begin() as connection:
    message = ""
    cart = connection.execute(sqlalchemy.text("""
        SELECT *
        FROM carts
        WHERE cart_id = :cart_id
        """), {"cart_id": cart_id}).first()
    # cart has been created
    if cart:
      cart_items = connection.execute(sqlalchemy.text("""
          SELECT *
          FROM cart_items
          WHERE cart_id = :cart_id
          """), {"cart_id": cart_id}).fetchall()
      # cart has been set
      if cart_items:
        # cart has been checked out
        if cart.payment:
          message = f"Cart #{cart.cart_id}: {cart.customer} used {cart.payment} to buy:"
        # cart has not been checked out
        else:
          message = f"Cart #{cart.cart_id}: {cart.customer} is seeking to buy:"
        for cart_item in cart_items:
          potion_inventory = connection.execute(sqlalchemy.text("""
              SELECT *
              FROM potion_inventory
              WHERE sku = :sku
              """), {"sku": cart_item.sku}).first()
          message += f" {cart_item.quantity} {cart_item.sku} ({potion_inventory.potion_type}) "\
                     f"for {cart_item.quantity * potion_inventory.price} gold "\
                     f"({potion_inventory.num_potion} remaining),"
        return message[:-1] + "."
    # cart has not been created
    else:
      return f"Cart #{cart_id} has not yet been created."


class CartItem(BaseModel):
  quantity: int


# don't know if cart_id and item_id are supposed to be diff. multiple items in 1 cart?
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
  """ """
  with db.engine.begin() as connection:
    connection.execute(sqlalchemy.text("""
        INSERT INTO cart_items (cart_id, sku, quantity)
        VALUES (:cart_id, :sku, :quantity)
        """), {"cart_id": cart_id, "sku": item_sku, "quantity": cart_item.quantity})
  return "OK"


class CartCheckout(BaseModel):
  payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
  """ """
  with db.engine.begin() as connection:
    total_potions_bought = 0
    total_gold_paid = 0
    cart = connection.execute(sqlalchemy.text("""
        SELECT sku, quantity
        FROM cart_items
        WHERE cart_id = :cart_id
        """), {"cart_id": cart_id}).fetchall()
    for cart_items in cart:
      potion_inventory = connection.execute(sqlalchemy.text("""
          SELECT *
          FROM potion_inventory
          WHERE sku = :sku
          """), {"sku": cart_items.sku}).first()
      # update gold in global_inventory
      connection.execute(sqlalchemy.text("""
          UPDATE global_inventory
          SET gold = gold + :gold_received
          """), {"gold_received": cart_items.quantity * potion_inventory.price})
      # update num_potion in potion_inventory
      connection.execute(sqlalchemy.text("""
          UPDATE potion_inventory
          SET num_potion = num_potion +- :num_bought
          WHERE sku = :sku
          """), {"num_bought": cart_items.quantity, "sku": cart_items.sku})
      total_potions_bought += cart_items.quantity
      total_gold_paid += cart_items.quantity * potion_inventory.price
    # add payment to cart to confirm
    connection.execute(sqlalchemy.text("""
        UPDATE carts
        SET payment = :payment
        WHERE cart_id = :cart_id
        """), {"payment": cart_checkout.payment, "cart_id": cart_id})
    connection.commit()
    print(get_cart(cart_id))
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
  