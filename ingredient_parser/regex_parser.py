#!/usr/bin/env python3

import re
from itertools import chain

from .parsers import ParsedIngredient
from .preprocess import PreProcessor

UNITS = {
    "tablespoon": ["tbsp", "tbsps", "tablespoon", "tablespoons", "Tbsp"],
    "teaspoon": ["tsp", "tsps", "teaspoon", "teaspoons"],
    "gram": ["g", "gram", "grams", "g can", "g cans", "g tin", "g tins"],
    "kilogram": ["kg", "kilogram", "kilograms"],
    "liter": ["l", "liter", "liters", "litre", "litres"],
    "milliliter": ["ml", "milliliter", "milliliters"],
    "pinch": ["pinch", "pinches"],
    "handful": ["handful", "handfuls"],
    "clove": ["cloves", "clove"],
    "sprig": ["sprig", "sprigs"],
    "stick": ["stick", "sticks"],
    "size": ["small", "medium", "large"],
    "dimension": ["cm", "inch", "'"],
    "cup": ["cup", "cups", "mug", "mugs"],
    "bunch": ["bunches", "bunch"],
    "rasher": ["rasher", "rashers"],
    "ounce": ["ounce", "ounces", "oz", "oz."],
    "pound": ["pound", "pounds", "lb", "lbs", "lb.", "lbs."],
}
UNITS_LIST = list(chain.from_iterable(UNITS.values()))
UNITS_LIST.sort(key=lambda x: len(x), reverse=True)

# This matches an integer, decimal number, fraction or range (i.e. 1-2)
QUANTITY_RE = r"""
(?P<quantity>(?:        # Creates a match group called quantity. Match everything inside the parentheses
(^\d+\s*x\s)?           # Optional capture group that matches e.g. 1x or 1 x followed by a space
\d+                     # Match at least one number
([\.\-]\d+)?           # Optionally matches a decimal point followed by at least one number, or a - followed by at least one number
))
"""
# This matches any string in the list of units
UNITS_RE = rf"""
(?P<unit>(?:            # Creates a match group called unit
{"|".join(UNITS_LIST)}  # Join all ingredients into a giant OR list
)\s)                    # Match a single whitespace character
?                       # Make this match group optional
"""
# Create full ingredient parse regular expression
PARSER_RE = rf"""
{QUANTITY_RE}           # Use QUANTITY_RE from above
\s*                     # Match zero or more whitespace characters
{UNITS_RE}              # Use UNITS_RE from above
(?P<name>(?:.*))        # Match zero of more characters in a match group called name
"""
# Precompile parser regular expression
PARSER_PATTERN = re.compile(PARSER_RE, re.VERBOSE)


def parse_ingredient_regex(sentence: str) -> ParsedIngredient:
    """Parse an ingredient senetence using regular expression based approach to return structured data

    Parameters
    ----------
    sentence : str
        Ingredient sentence to parse

    Returns
    -------
    ParsedIngredient
        Dictionary of structured data parsed from input string

    Examples
    --------
    >>> parse_ingredient_regex("2 yellow onions, finely chopped")
    {'sentence': '2 yellow onions, finely chopped', 'quantity': '2', 'unit': '', 'name': 'yellow onions', 'comment': 'finely chopped', 'other': ''}

    >>> parse_ingredient_regex("100 ml milk")
    {'sentence': '100 ml milk', quantity': '100', 'unit': 'ml', 'name': 'milk', 'comment': '', 'other': ''}

    >>> parse_ingredient_regex("1 onion, finely chopped")
    {'sentence': '1 onion, finely chopped', quantity': '1', 'unit': '', 'name': 'onion', 'comment': 'finely chopped', 'other': ''}

    >>> parse_ingredient_regex("2 1/2 cups plain flour")
    {'sentnece': '2 1/2 cups plain flour', quantity': '2.5', 'unit': 'cups', 'name': 'plain flour', 'comment': '', 'other': ''}

    """
    parsed: ParsedIngredient = {
        "sentence": sentence,
        "quantity": "",
        "unit": "",
        "name": "",
        "comment": "",
        "other": "",
    }

    processed_sentence = PreProcessor(sentence)
    res = PARSER_PATTERN.match(processed_sentence.sentence)
    if res is not None:

        parsed["quantity"] = (res.group("quantity") or "").strip()
        parsed["unit"] = (res.group("unit") or "").strip()

        # Split name by comma, but at most one split
        # This is attempt to split the comment from the name
        name = res.group("name" or "").split(",", 1)
        if len(name) > 1:
            parsed["name"] = name[0].strip()
            parsed["comment"] = name[1].strip()
        else:
            parsed["name"] = name[0].strip()

    return parsed
