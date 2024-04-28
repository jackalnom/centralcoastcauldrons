import io
import re
from fastapi import HTTPException, status

COLORS = ["red", "green", "blue", "dark"]


# TODO: add more colors and find more efficient way / less hardcoded
def get_potion_type(color: str):
    potion_type = None
    lower_color = color.lower()
    lower_color.find
    if ('red' in lower_color):
        potion_type = [100, 0, 0, 0]
    elif ('green' in lower_color):
        potion_type = [0, 100, 0, 0]
    elif ('blue' in lower_color):
        potion_type = [0, 0, 100, 0]
    elif ('dark' in lower_color):
        return potion_type

def get_color(potion_type: list[int]) -> str:

    if (len(potion_type) != 4) or not potion_type:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incorrect potion_type passed."
        )
    # TODO: more efficient implementation, using hashtable???
    color_str = ""
    colors = ['red', 'green', 'blue']
    for idx in range(len(potion_type)):
        if potion_type[idx] == 100:
            color_str += colors[idx] + "_"
    if (len(color_str)) == 0:
        return ''
    return color_str[:len(color_str) -1]

def sku_to_db_col(potion_sku: str) -> str:
    # ONLY matches three conditons, will be deprecated soon
    if (potion_sku == "green potion"):
        return "num_green_potions"
    elif (potion_sku == "red potion"):
        return "num_red_potions"
    else:
        return "num_blue_potions"

def potion_type_name(potion_type: list[int]):
    if (len(potion_type) != 4):
        raise Exception("Invalid length passed. Must be 4, (red, green, blue, dark).") 
    
    name = ""

    # see how many words we will need to match
    for idx in range(len(potion_type)):
        # will derive values from 4 different files
        if (potion_type[idx] != 0):
            with open(f"potion_names/{COLORS[idx]}.csv") as potion_names:
                for _ in range(potion_type[idx] - 1):
                    next(potion_names)
                name += potion_names.readline().strip('\n') + " "
    name += "Potion"
    return name


    
def idx_to_color(idx: int):
    if idx == 0:
        return 'red'
    elif idx == 1:
        return 'green'
    elif idx == 2:
        return 'blue'
    elif idx == 3:
        return 'dark'
    raise ValueError("Incorrect idx range passed (0-3).")
