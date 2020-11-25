
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
        i = i + 1
    if i == length:
        return 'value not found'
    else:
        return i


def clean_intents(intents: list) -> list:
    """
    Some intents may trigger actions which means they will be dict instead of strings.
    This method parses those dicts and returns the list of intents.



    Args:
        intents (list): list of intents taken from the domain
    Example: [{'start_dialogue': {'triggers': 'action_check_Bot_Introduced'}}, 'greeting', ]

    Returns:
        list: list of intents without dicts
    Example: ['start_dialogue', 'greeting', ]
    """

    for i, intent in enumerate(intents):
        if isinstance(intent, dict):
            intents[i] = list(intent.keys())[0]

    return intents
