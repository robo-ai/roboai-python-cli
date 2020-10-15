
def get_index(lista: list, value: str) -> int:
    """
    Gets the list index of a given value if it exists.
    :lista: list to get the index from
    :value: value to search in the list
    :return i: index of the value in the list
    """
    i = 0
    length = len(lista)
    while i < length and lista[i]['name'] != value:
        i = i+1
    if i == length:
        return 'value not found'
    else:
        return i
