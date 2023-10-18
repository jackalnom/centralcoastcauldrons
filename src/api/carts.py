from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src.api.database import engine as db
from src.api.models import Cart, CartModel, Inventory, PotionsInventory, CartItem as CartItemType

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
    cart_model = CartModel(db.engine)
    cart_id = cart_model.create_cart(new_cart.customer).cart_id
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return CartModel(db.engine).get_entry(cart_id)


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    entries = PotionsInventory(db.engine).get_inventory()
    for entry in entries:
        if entry[3] == item_sku:
            print(entry)
            item = CartItemType(quantity=cart_item.quantity,potion=entry[0])
            cm = CartModel(db.engine)
            cart = cm.get_entry(cart_id)
            print(cart)
            print("item",item)
            cart.items.append(item)
            cm.update_cart(cart)
            return "OK"
    return "Invalid SKU"


class CartCheckout(BaseModel):
    payment: str

def process_checkout(cart: Cart, cart_checkout: CartCheckout,potion_entries):
    """ """
    gold_paid = 0
    print(cart)
    print(cart_checkout)
    potions_bought = []
    print(potion_entries)
    for item in cart.items:
        for potion_entry in potion_entries:
            if potion_entry[0] == item.potion:
                potions_bought.append([potion_entry[1], item.quantity, potion_entry[4]])
                break
    print(potions_bought)

    gold_paid = sum([potion_entry[2] * potion_entry[1] for potion_entry in potions_bought])
    return gold_paid , potions_bought


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print(f"checkout {cart_id} {cart_checkout}")
    cm = CartModel(db.engine)
    cart = cm.get_entry(cart_id)

    # total_potions = sum([item["quantity"] for _,item in enumerate(cart.get("items",{}))])
    total_potions = 0

    potions = PotionsInventory(db.engine)
    

    gold_paid, potions_bought = process_checkout(cart, cart_checkout, potions.get_inventory())
    print(potions_bought)

    total_potions += sum([potion_entry[1] for potion_entry in potions_bought])
    inventory = Inventory(db.engine)
    inventory.fetch_inventory()
    inventory.set_inventory(inventory.gold + gold_paid, inventory.num_red_ml, inventory.num_blue_ml, inventory.num_green_ml)
    inventory.sync()
    for potion in potions_bought:
        print(potion)
        potions.update_quantity(potion[0], potions.get_entry(potion[0])[2] - potion[1])

    return {"total_potions_bought": total_potions, "total_gold_paid": gold_paid}
