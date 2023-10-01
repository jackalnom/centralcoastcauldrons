from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from ..models.global_inventory import GlobalInventory, PotionInventory
from ..models.cart import Cart

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    GlobalInventory.get_singleton().reset()
    Cart.delete_all_carts()
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    #TODO: implement get_shop_info
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Lit Potion Muh Town",
        "shop_owner": "Potion King of Muh Town (Alfred)",
    }

