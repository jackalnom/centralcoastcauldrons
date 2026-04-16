from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from enum import Enum
from typing import List, Optional
from src.api.helper import add_global_inventory, add_potion, get_global_inventory, get_potion
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class SearchSortOptions(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class LineItem(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: int
    timestamp: str


class SearchResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[LineItem]


@router.get("/search/", response_model=SearchResponse, tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.timestamp,
    sort_order: SearchSortOrder = SearchSortOrder.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.
    """
    return SearchResponse(
        previous=None,
        next=None,
        results=[
            LineItem(
                line_item_id=1,
                item_sku="1 oblivion potion",
                customer_name="Scaramouche",
                line_item_total=50,
                timestamp="2021-01-01T00:00:00Z",
            )
        ],
    )


cart_id_counter = 1
carts: dict[int, dict[str, int]] = {}


class Customer(BaseModel):
    customer_id: str
    customer_name: str
    character_class: str
    character_species: str
    level: int = Field(ge=1, le=20)


@router.post("/visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_visits(visit_id: int, customers: List[Customer]):
    """
    Shares the customers that visited the store on that tick.
    """
    return customers[visit_id]


class CartCreateResponse(BaseModel):
    cart_id: int


@router.post("/", response_model=CartCreateResponse)
def create_cart(new_cart: Customer):
    """
    Creates a new cart for a specific customer.
    """

    with db.engine.begin() as connection:
        id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart_checkout (customer_id, customer_name, customer_species, customer_class)
                VALUES (:customer_id, :customer_name, :customer_species, :customer_class)
                RETURNING id;
                """),
                [{"customer_id": new_cart.customer_id, "customer_name" : new_cart.customer_name, "customer_species" : new_cart.character_species, "customer_class" : new_cart.character_class}])
    id = id.fetchone().id # type: ignore
    return CartCreateResponse(cart_id=id)


class CartItem(BaseModel):
    quantity: int = Field(ge=1, description="Quantity must be at least 1")


@router.post("/{cart_id}/items/{item_sku}", status_code=status.HTTP_204_NO_CONTENT)
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    print(
        f"cart_id: {cart_id}, item_sku: {item_sku}, cart_item: {cart_item}, carts: {carts}"
    )
    if cart_id not in carts:
        raise HTTPException(status_code=404, detail="Cart not found")

    with db.engine.begin() as connection:
        potion_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM potion_inventory
                WHERE item_sku = :item_sku;
                """),
                [{"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity}])
        potion_id = potion_id.fetchone().id  # type: ignore
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart_inventory (cart_id, potion_id, quantity)
                VALUES (:cart_id, :potion_id, :quantity)
                """),
                [{"cart_id": cart_id, "potion_id": potion_id, "quantity": cart_item.quantity}])

    return status.HTTP_204_NO_CONTENT


class CheckoutResponse(BaseModel):
    total_potions_bought: int
    total_gold_paid: int


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout", response_model=CheckoutResponse)
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """
    Handles the checkout process for a specific cart.
    """

    if cart_id not in carts:
        raise HTTPException(status_code=404, detail="Cart not found")

    with db.engine.begin() as connection:
        checkout = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM cart_checkout
                WHERE id = :id;
                """),
                [{"id": id}])
    total_potions_bought = 0
    # Remove potions
    for potion in checkout:
        total_potion_bought += potion.quantity
        add_potion(potion.potion_id, get_potion(potion.id).quantity)

    total_gold_paid = total_potions_bought * 100  # Assuming each potion costs 75 gold

    # Checkout transation: add gold
    add_global_inventory("gold", total_gold_paid)


    return CheckoutResponse(
        total_potions_bought=total_potions_bought, total_gold_paid=total_gold_paid
    )
