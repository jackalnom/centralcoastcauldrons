colors = ["red", "green", "blue"]


def get_base_potion_type(color):
    lookup = {"red": [1, 0, 0, 0], "green": [0, 1, 0, 0], "blue": [0, 0, 1, 0]}
    return lookup[color]


def get_color_from_potion_type(potion_type):
    for i in range(len(colors)):
        if potion_type[i] == 1:
            return colors[i]
    raise Exception(f"could not find color from {potion_type}")
