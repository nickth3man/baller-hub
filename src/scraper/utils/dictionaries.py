def merge_two_dicts(first, second):
    """
    Merges two dictionaries into a new dictionary.

    If keys collide, values from the `second` dictionary overwrite those in `first`.

    Args:
        first (dict): The base dictionary.
        second (dict): The dictionary to merge on top.

    Returns:
        dict: A new dictionary containing merged key-value pairs.
    """
    combined = first.copy()
    combined.update(second)
    return combined
