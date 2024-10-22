import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

#i did this:
#create cartLineItem table
# CartLineItem
# cart_id | potion_id | quantity

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

#don't need to do this yet
class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

#
##
#add dictionary for the carts
carts = {}
cart_key = 0
##
#

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

    #added below
    with db.engine.begin() as connection:
        
        sqlpotion = "SELECT num_green_potion FROM global_inventory"
        
        num_potions = connection.execute(sqlalchemy.text(sqlpotion)).scalar()
        
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


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

#dont need to do visits yet
@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    #added below
    #with db.engine.begin() as connection:
    #    result = connection.execute(sqlalchemy.text(sql_to_execute))
        
    return "OK"



@router.post("/")
def create_cart(new_cart: Customer):
    """Create a new cart!"""


    #start id at 0, increment
    global cart_key
    carts[cart_key] = {}
    cart_key +=1

    return {"cart_id": cart_key - 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """Set the quantity of an item in the cart"""
#don't need sql rn in this function

    #with db.engine.begin() as connection:
    #    result = connection.execute(sqlalchemy.text(sql_to_execute))

#item sku is [0]
#quantity is [1]

    if cart_id not in carts:
        return "Error! Cart not found."

    carts[cart_id] = {item_sku, cart_item.quantity} 
        
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """Checkout cart!"""

    if cart_id not in carts:
        return "Error! Cart not found."

    total_gold_paid = 0


    with db.engine.begin() as connection:
    #item sku is [0]
    #quantity is [1]
        #item_sku = carts[cart_id][0]

        for item_sku, quantity in carts[cart_id].items():
            mlamt = quantity * 100 #100 ml per potion
            goldamt = quantity * 100 #40 is the gold price
            totalgoldpaid += goldamt

        #subtract ml from inventory
        if(carts[cart_id][0] == "RED_POTION_0"):
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml =  num_red_ml - {mlamt}"))

        if(carts[cart_id][0] == "GREEN_POTION_0"):
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml =  num_green_ml - {mlamt}"))

        if(carts[cart_id][0] == "BLUE_POTION_0"):
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml =  num_blue_ml - {mlamt}"))

        #add gold based on how many potions bought 
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold =  gold + {goldperquantity}"))

       
       #notes
        #newgoldsql = 
        #newgold = connection.execute(sqlalchemy.text(newgoldsql)).scalar()

#decrement amt of potions, increment gold (in sql statement)
      #the only place in carts where i need sql rn 

    return {"total_potions_bought": carts[cart_id][1], "total_gold_paid": goldperquantity}