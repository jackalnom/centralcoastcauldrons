from src.api.admin import reset
from src.api.catalog import *
from src.api.inventory import *
def test_catalog() -> None:
    reset()
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 1000,
                red_ml = 400,
                green_ml = 100,
                blue_ml = 200,
                dark_ml = 100
                """
            )
        )

    inventory = get_inventory()
    assert inventory.gold == 1000 and inventory.number_of_potions == 0 and inventory.ml_in_barrels == 800
    
    catalog = get_catalog()
    assert len(catalog) == 0
    reset()
    
