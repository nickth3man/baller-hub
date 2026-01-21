def str_to_int(value, default=0):
    """
    Safely converts a string to an integer.

    Args:
        value (str): The string to convert.
        default (int): Value to return if conversion fails. Defaults to 0.

    Returns:
        int: The converted integer or the default value.
    """
    stripped_value = value.strip()
    try:
        return int(stripped_value)
    except ValueError:
        return default


def str_to_float(value, default=float(0)):
    """
    Safely converts a string to a float.

    Args:
        value (str): The string to convert.
        default (float): Value to return if conversion fails. Defaults to 0.0.

    Returns:
        float: The converted float or the default value.
    """
    stripped_value = value.strip()
    try:
        return float(stripped_value)
    except ValueError:
        return default
