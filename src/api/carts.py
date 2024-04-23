from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc" 


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

# used for global list of carts
# items : list of tuples of (potion_sku, quantity)
class Cart(BaseModel):  
    cart_id: int = None
    items: list[tuple] = []
    customer: Customer = None

# global list of carts
carts_array: list[Cart] = []


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


# class Customer(BaseModel):
#     customer_name: str
#     character_class: str
#     level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    print("CALLED post_visits()")
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    print("CALLED create_cart()")
    """ """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""INSERT INTO carts (
                                                        customer_name,
                                                        character_class,
                                                        level
                                                    )  
                                                    VALUES (:name, :class, :level)
                                                    RETURNING id"""),
                                                    [{"name": new_cart.customer_name, 
                                                      "class": new_cart.character_class, 
                                                      "level": new_cart.level}])
        
    return {"cart_id": result.fetchone().id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    print("CALLED set_item_quantity()")
    """ """
    # get cart by cart_id
    if len(carts_array) > cart_id:
        cart = carts_array[cart_id]
    else:
        return "FAILED"
    
    # add item with quantity to items list in cart
    entry = (item_sku, cart_item.quantity)
    cart.items.append(entry)
    print(carts_array)

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    print("CALLED checkout()")
    if cart_id >= len(carts_array):
        return "FAILED"
    
    total_num_potions = num_green_p = num_red_p = num_blue_p = gold_payment = 0
    
    cart = carts_array[cart_id]
    for item in cart.items:
        if item[0] == "GREEN_POTION_0":
            num_green_p += item[1]
            gold_payment += item[1] * 35
        elif item[0] == "RED_POTION_0":
            num_red_p += item[1]
            gold_payment += item[1] * 35
        elif item[0] == "BLUE_POTION_0":
            num_blue_p += item[1]
            gold_payment += item[1] * 35
        total_num_potions += item[1]

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = num_green_potions - {num_green_p}, num_red_potions = num_red_potions - {num_red_p}, num_blue_potions = num_blue_potions - {num_blue_p}, gold = gold + {gold_payment}"))
    print(f"Cart {cart_id} successfully purchased {total_num_potions} potions and paid {gold_payment} gold.")

    return {"total_potions_bought": total_num_potions, "total_gold_paid": gold_payment}
