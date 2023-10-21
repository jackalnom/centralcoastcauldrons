from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime


router = APIRouter(
  prefix="/carts",
  tags=["cart"],
  dependencies=[Depends(auth.get_api_key)],
)


convert_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


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
    day = convert_days[datetime.now().weekday()]
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
          potion = connection.execute(sqlalchemy.text(f"""
              SELECT potions.{day}_price as price, potions.potion_type, COALESCE(SUM(change), 0) as num_potion
              FROM potions
              LEFT JOIN potion_entries ON potion_entries.potion_sku = potions.sku
              WHERE potions.sku = :sku
              GROUP BY potions.{day}_price, potions.potion_type
              """), {"sku": cart_item.sku}).first()
          message += f" {cart_item.quantity} {cart_item.sku} ({potion.potion_type}) "\
                     f"for {cart_item.quantity * potion.price} gold "\
                     f"({potion.num_potion} remaining),"
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
  # add payment to cart to confirm
  with db.engine.begin() as connection:
    global_transaction_id = connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_transactions DEFAULT VALUES
        RETURNING id
        """)).first().id
    connection.execute(sqlalchemy.text("""
        UPDATE carts
        SET payment = :payment, global_inventory_transaction_id = :transaction_id
        WHERE cart_id = :cart_id
        """), {"payment": cart_checkout.payment, "transaction_id": global_transaction_id, "cart_id": cart_id})
  with db.engine.begin() as connection:
    day = convert_days[datetime.now().weekday()]
    total_potions_bought = 0
    total_gold_paid = 0
    cart = connection.execute(sqlalchemy.text("""
        SELECT sku, quantity
        FROM cart_items
        WHERE cart_id = :cart_id
        """), {"cart_id": cart_id}).fetchall()
    for cart_items in cart:
      potion = connection.execute(sqlalchemy.text("""
          SELECT *
          FROM potions
          WHERE sku = :sku
          """), {"sku": cart_items.sku}).first()
      total_potions_bought += cart_items.quantity
      total_gold_paid += cart_items.quantity * getattr(potion, day + "_price")
      # update potion_inventory
      potion_transaction_id = connection.execute(sqlalchemy.text("""
          INSERT INTO potion_transactions (description)
          VALUES (:description)
          RETURNING id
          """), {"description": get_cart(cart_id)}).first().id
      connection.execute(sqlalchemy.text("""
          INSERT INTO potion_entries (potion_sku, change, potion_transaction_id)
          VALUES (:potion_sku, :change, :transaction_id)
          """), {"potion_sku": cart_items.sku, "change": -cart_items.quantity, "transaction_id": potion_transaction_id})
      # update potions num_sold for day
      #TODO maybe make this have ledger? not necessary since already logged
      connection.execute(sqlalchemy.text(f"""
          UPDATE potions
          SET {day}_sold = {day}_sold + :num_sold
          WHERE sku = :sku
          """), {"num_sold": cart_items.quantity, "sku": cart_items.sku})
    # update global_inventory
    connection.execute(sqlalchemy.text("""
        UPDATE global_inventory_transactions
        SET description = :description
        WHERE id = :transaction_id
        """), {"description": get_cart(cart_id), "transaction_id": global_transaction_id})
    connection.execute(sqlalchemy.text("""
        INSERT INTO global_inventory_entries (change_gold, global_inventory_transaction_id)
        VALUES (:total_gold_paid, :transaction_id)
        """), {"total_gold_paid": total_gold_paid, "transaction_id": global_transaction_id})
    connection.commit()
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
