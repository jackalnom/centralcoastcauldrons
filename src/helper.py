from fastapi import HTTPException, status
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