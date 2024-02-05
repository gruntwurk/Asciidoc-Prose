"""
Utility code for dealing with cooking recipes.
"""
import re
from .prose_utils import (FRACTION_ATTRIBUTES, fix_fractions, fix_temperature_degrees)


COOKING_ATTRIBUTES = """
:tsp: teaspoon
:tbsp: tablespoon
:c: cup
:oz: ounce
:lb: pound
:sptt: <<salt,Salt>> and <<pepper,pepper>> to taste.
:voil: cooking <<oil,oil>>
:evoo: extra-virgin <olive-oil,olive oil>>
"""

def recipe_fixup(txt):
    """
    Takes the text of a random recipe clipping and standardizes it.
    """

    # remove tabs so that we only have to worry about spaces
    txt = re.sub(r"\t", " ", txt)

    # Convert fractions to attributes
    txt = fix_fractions(txt)

    # Standardize to use the degree symbol
    txt = fix_temperature_degrees(txt)

    # Convert units to attributes
    # (No trailing \b on purpose to allow for plurals)
    txt = re.sub(r"\btsp|teaspoon","{tsp}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\btbsp|tablespoon","{tbsp}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\boz|ounce","{oz}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\blb|pound","{lb}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bcup","{c}", txt, flags=re.IGNORECASE)

    # Standardize common ingredients
    txt = re.sub(r"salt (and|&) pepper to taste\.?","{sptt}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"(cooking|vegetable|canola) oil?","{voil}", txt, flags=re.IGNORECASE)
    txt = re.sub(r"(extra[- ])?virgin olive oil?","{evoo}", txt, flags=re.IGNORECASE)

    # Let AsciiDoc do the step numbering
    txt = re.sub(r"^ *step *\d+[).:]?\s*", ". ", txt, flags=re.MULTILINE+re.IGNORECASE)
    txt = re.sub(r"^ *\d+\[).:] *", ". ", txt, flags=re.MULTILINE)

    # Remove extraneous lines
    txt = re.sub(r"^ *(make the recipe with us|add to your grocery list|ingredient substitution guide|nutritional information|us customary|metric|1x|2x|3x|jump to recipe|print recipe|pin recipe|jump to video|video|watch|podcast|articles|shop|log in) *$", "", txt, flags=re.MULTILINE+re.IGNORECASE)

    # Recipe Title (chapter heading)
    txt = re.sub(r"^(.* Recipe) *$", r"== \1", txt, flags=re.MULTILINE+re.IGNORECASE)

    # Sub-headings
    txt = re.sub(r"^ *(ingredients|preparation|instructions|directions|notes|nutrition) *$", r"=== \1", txt, flags=re.MULTILINE+re.IGNORECASE)

    return COOKING_ATTRIBUTES + FRACTION_ATTRIBUTES + txt
