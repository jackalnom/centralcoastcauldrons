def potion_type_tostr(potion_type):
    return "{" + ",".join(map(str, potion_type)) + "}"

def list_floor_division(list1, list2):
    if len(list1) != len(list2):
        raise ValueError("Lists must be of the same length")
    available = []
    for i in range(len(list1)):
        if list2[i] == 0:
            continue
        available.append(list1[i] // list2[i])
    return min(available)