from src.api.bottler import create_bottle_plan


def test_bottle_red_potions():
    red_ml = 100
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    maximum_potion_capacity = 50
    current_potion_inventory: list = []

    result = create_bottle_plan(
        red_ml=red_ml,
        green_ml=green_ml,
        blue_ml=blue_ml,
        dark_ml=dark_ml,
        maximum_potion_capacity=maximum_potion_capacity,
        current_potion_inventory=current_potion_inventory,
    )

    assert len(result) == 1
    assert result[0].potion_type == [100, 0, 0, 0]
    assert result[0].quantity == 5
