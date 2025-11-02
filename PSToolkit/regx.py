"""
# Regex Helpers

* Description:

    mHelper library for common regex functions used within the toolkit.
    Typically meant to sort items or paths.
"""


import re


def natural_sort_strings(items: list[str]):
    """
    Sort the given list in the way that humans expect.

    Args:
        list[str]: The list of strings to sort.
    """
    # Copied from studio library
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split(r'([0-9]+)', key)]
    items.sort(key=alphanum_key)


def validation_no_special_chars(string: str) -> bool:
    """
    Checks a string to see if it contains non-alpha-numeric or non-underscore characters.
    Will return True if the string contains no special characters. Will return False
    if the string contains special characters or is an empty string.

    Args:
        string (str): The string to check against.

    Returns:
        bool: Whether the string contains no special characters.

    Notes:
        A common gotcha is that whitespace counts as a special character.
    """
    m = re.match(r'^[a-zA-Z0-9_]*$', string)
    if m and string != '':
        return True
    else:
        return False
