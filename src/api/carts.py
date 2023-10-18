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

# TODO impliment multicolor and new cart system
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("Attempting to generate cart...")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"INSERT INTO carts(customer_name) \
                                                      VALUES ('{new_cart.customer}') \
                                                      RETURNING cart_id"))
        cart_id = result.first()[0]
    print(f"Cart Generated with ID: {cart_id}")
    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"INSERT INTO carts_transactions(cart_id, sku, quantity) \
                                                      VALUES ({cart_id}, '{item_sku}', {cart_item.quantity})"))
    print(f"Added {cart_item.quantity} of {item_sku} to cart {cart_id}...")

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    # this sucks, need to redo eventually
    total_quantity = 0
    total_cost = 0
    
    # update gold
    with db.engine.begin() as connection:
        result= connection.execute(sqlalchemy.text(
            "INSERT INTO stock_ledger (d_gold, :description) \
            SELECT d_gold \
            FROM \
                ( \
                SELECT carts_transactions.quantity * potion_inventory.cost as d_gold \
                FROM carts_transactions \
                JOIN potion_inventory on potion_inventory.sku = carts_transactions.sku \
                WHERE carts_transactions.cart_id = :cart_id \
                ) \
            as subquery \
            RETURNING d_gold;"), 
            [{
                'description':f"Checkout Cart {cart_id} with payment {cart_checkout.payment}",
                'cart_id':cart_id
            }])
    total_cost = result.first()[0]
    
    with db.engine.begin() as connection:
        result= connection.execute(sqlalchemy.text(
            "INSERT into potion_ledger (d_quan, potion_id, description) \
            SELECT (-1*carts_transactions.quantity) as d_quan, potion_inventory.id as potion_id, :description as description\
            FROM carts_transactions \
            JOIN potion_inventory on potion_inventory.sku = carts_transactions.sku \
            WHERE carts_transactions.cart_id = :cart_id) \
            RETURNING d_quan"), 
            [{
                'description':f"Checkout Cart {cart_id}",
                'cart_id':cart_id
            }])
    for row in result:
        total_quantity += (-1)*row[0]


    print(f"Cart ID {cart_id} purchased {total_quantity} potions and paid {total_cost} gold")

    return {"total_potions_bought": total_quantity, "total_gold_paid": total_cost}
