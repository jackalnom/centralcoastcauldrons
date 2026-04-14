from src.api.bottler import *
from src.api.admin import reset

from typing import List

from src.api.helper import get_potion_count, get_potion_inventory, increase_potions


def test_potion_variance() -> None:
    reset()
    with db.engine.begin() as connection:
        potions = connection.execute(
            sqlalchemy.text(
                """
                SELECT id from potion_inventory
                """
            )
        )
    assert len(potions.fetchall()) == 35
    assert len(get_potion_inventory()) == 0
    assert get_potion_count() == 0

    increase_potions(1, 10)
    assert get_potion_count() == 10
    increase_potions(10, 10)
    assert get_potion_count() == 20
    assert len(get_potion_inventory()) == 2