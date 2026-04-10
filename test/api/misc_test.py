from src.api.admin import reset
from src.api.catalog import *
from src.api.inventory import *
def test_catalog() -> None:

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 1000,
                red_ml = 400,
                green_ml = 100,
                blue_ml = 200,
                red_potions = 2,
                green_potions = 3,
                blue_potions= 1
                """
            )
        )
    
    catalog = get_catalog()
    assert catalog[0].quantity == 2
    assert catalog[1].quantity == 3
    assert catalog[2].quantity == 1
    assert catalog[0].price == 75
    assert catalog[1].price == 75
    assert catalog[2].price == 75

    inventory = get_inventory()
    assert inventory.gold == 1000 and inventory.number_of_potions == 6 and inventory.ml_in_barrels == 700

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 1000,
                red_ml = 400,
                green_ml = 100,
                blue_ml = 200,
                red_potions = 2,
                green_potions = 0,
                blue_potions= 0
                """
            )
        )

    inventory = get_inventory()
    assert inventory.gold == 1000 and inventory.number_of_potions == 2 and inventory.ml_in_barrels == 700
    
    catalog = get_catalog()
    assert len(catalog) == 1
    reset()
    
