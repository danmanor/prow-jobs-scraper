def str_to_bool(string: str):
    """Converts a string to its boolean representation.

    Args:
        string: The string to be converted.

    Returns:
        The boolean representation of the string.

    Raises:
        ValueError: If the string does not have a valid boolean representation.
    """
    true_values = ["true", "yes", "y", "1", "t"]
    false_values = ["false", "no", "n", "0", "f"]

    normalized = string.strip().lower()

    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert {string} to a bool")
