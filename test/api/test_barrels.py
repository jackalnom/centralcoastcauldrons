import sqlalchemy

from src.api.barrels import (
    calculate_barrel_summary,
    create_barrel_plan,
    Barrel,
    BarrelOrder,
)
from typing import List
from src.api.admin import reset
from src import database as db
from src.api.barrels import *


def test_barrel_delivery() -> None:
    reset()

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 1000,
                red_ml = 400,
                blue_ml = 200,
                green_ml = 100,
                dark_ml = 300
                """
            )
        )
    delivery: List[Barrel] = [
        Barrel(
            sku="SMALL_RED_BARREL",
            ml_per_barrel=1000,
            potion_type=[1.0, 0, 0, 0],
            price=100,
            quantity=10,
        ),
        Barrel(
            sku="SMALL_GREEN_BARREL",
            ml_per_barrel=1000,
            potion_type=[0, 1.0, 0, 0],
            price=150,
            quantity=5,
        ),
    ]

    delivery_summary = calculate_barrel_summary(delivery)
    assert len(create_barrel_plan(1500, 100, 100, 100, 100, 100, delivery)) == 2

    assert delivery_summary.gold_paid == 1750


def test_barrel_plan() -> None:
    wholesale_catalog: List[Barrel] = [
        Barrel(
            sku="SMALL_RED_BARREL",
            ml_per_barrel=1000,
            potion_type=[1.0, 0, 0, 0],
            price=50,
            quantity=10,
        ),
        Barrel(
            sku="SMALL_GREEN_BARREL",
            ml_per_barrel=1000,
            potion_type=[0, 1.0, 0, 0],
            price=50,
            quantity=5,
        ),
        Barrel(
            sku="SMALL_BLUE_BARREL",
            ml_per_barrel=1000,
            potion_type=[0, 0, 1.0, 0],
            price=50,
            quantity=2,
        ),
    ]

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET 
                gold = 1000,
                red_ml = 400,
                blue_ml = 200,
                green_ml = 100,
                dark_ml = 300
                """
            )
        )
    
    post_deliver_barrels(wholesale_catalog, 0)
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT gold, red_ml, green_ml, blue_ml, dark_ml
                FROM global_inventory
                """
            )
        ).one()
    assert row[0] == 150
    assert row[1] == 10400
    assert row[2] == 5100
    assert row[3] == 2200
    assert row[4] == 300

    plan = get_wholesale_purchase_plan(wholesale_catalog)[0]
    assert plan.quantity == 3
        


    reset()
    # Verify reset worked
    with db.engine.begin() as connection:
        table_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT gold, red_ml, green_ml, blue_ml, dark_ml
                FROM global_inventory  
                """
            )
        ).one()

    assert table_row[0] == 100
    for i in range(1, len(table_row)):
        assert table_row[i] == 0
