"""
General-Purpose Utilities for the AsciiDoc-Prose package.
"""

import re

# ###########################################################################
#                                                             Text Processing
# ###########################################################################


def pluck_out_match(txt, m, replacement="") -> str:
    return txt[:m.start(0)] + replacement + txt[m.end(0):]


def snake_case(identifier: str) -> str:
    """
    Converts CamelCase or javaCase to snake_case (all lower with underscores).
    """
    words = re.findall(r"([a-z]+|[A-Z][a-z]*|[^A-Za-z]+)",identifier)
    lower_words = [word.lower() for word in words if word != "_"]
    return "_".join(lower_words)


def camel_case(identifier: str) -> str:
    """
    Converts snake_case to CamelCase.
    """
    if not identifier:
        return ""
    words = identifier.split('_')
    camel_words = [word[0].upper() + word[1:].lower() for word in words]
    return "".join(camel_words)


def transpose(identifier: str) -> str:
    """
    Transposes the selected text.

    If the text contains space(s), then the first and last word of the selected
    text are transposed. Otherwise, the text is transposed around the first
    non-alphanumeric character found within the text.

    red green -> green red
    cat in the hat -> hat in the cat
    alpha-beta -> beta-alpha
    alpha_beta -> beta_alpha
    alpha___beta -> __beta_alpha

    """
    if not identifier:
        return ""

    # Transpose by words
    tokens = identifier.split(" ")
    if (token_count := len(tokens)) > 1:
        last_token_as_punctuated = re.match(r"(.*?)([,;\.\?!]?)$", tokens[token_count - 1])
        last_token_alone = last_token_as_punctuated[1]
        punctuation = last_token_as_punctuated[2]
        tokens[0], tokens[token_count-1] = last_token_alone, tokens[0] + punctuation
        return " ".join(tokens)

    # Transpose within a single identifier
    tokens = re.match(r"([A-Za-z0-9]*)(.)(.*)", identifier)
    return tokens[3] + tokens[2] + tokens[1]


def collapse_whitespace(txt: str) -> str:
    """
    Removes trailing spaces; collapses tabs and multiple spaces to a single space.
    """
    # remove tabs
    txt = re.sub(r"\t", " ", txt)

    # Remove any trailing spaces
    txt = re.sub(r" +$", "", txt, flags=re.MULTILINE)

    # Collapse multiple spaces
    txt = re.sub(r"  +", " ", txt)
    return txt


def generate_valid_anchor_token(descriptive_text: str, separator='-') -> str:
    """
    Converts the given descriptive text to a valid AsciiDoc anchor token
    (i.e. containing only lowercase letters, digits, dashes, and underscores.)
    """
    # Make it all lower case
    block_id = descriptive_text.lower()
    # Remove anything that's not a letter, digit, hyphen, underscore, or space,
    # then strip leading and trailing spaces
    block_id = re.sub(r'[^-0-9a-z _]', r'', block_id).strip()
    # Replace spaces with dashes (or whatever separator is specified)
    block_id = re.sub(r' +', separator, block_id)
    return block_id


# ###########################################################################
#                                                                   Numbering
# ###########################################################################

FRACTION_ATTRIBUTES = """
:half: ½
:third: ⅓
:two-thirds: ⅔
:quarter: ¼
:three-quarters: ¾
:eighth: ⅛
:three-eighths: ⅜
:five-eighths: ⅝
:seven-eighths: ⅞
"""


def fix_fractions(txt: str) -> str:
    # Convert fractions to attributes
    txt = re.sub(r"½|\b1/2\b", "{half}", txt)
    txt = re.sub(r"⅓|\b1/3\b", "{third}", txt)
    txt = re.sub(r"⅔|\b2/3\b", "{two-thirds}", txt)
    txt = re.sub(r"¼|\b1/4\b", "{quarter}", txt)
    txt = re.sub(r"¾|\b3/4\b", "{three-quarters}", txt)
    txt = re.sub(r"⅛|\b1/8\b", "{eighth}", txt)
    txt = re.sub(r"⅜|\b3/8\b", "{three-eighths}", txt)
    txt = re.sub(r"⅝|\b5/8\b", "{five-eighths}", txt)
    txt = re.sub(r"⅞|\b7/8\b", "{seven-eighths}", txt)
    return txt


def fix_temperature_degrees(txt: str) -> str:
    # Standardize temperatures to use the degree symbol
    # e.g. "123 degrees Fahrenheit" -> "123{deg}F"
    txt = re.sub(r"(\d+) *deg(\.|rees|s)? *f(ahrenheit|\.|\b)", r"\1{deg}F", txt, flags=re.IGNORECASE)
    txt = re.sub(r"(\d+) *deg(\.|rees|s)? *c(elsius|entigrade|\.|\b)", r"\1{deg}C", txt, flags=re.IGNORECASE)
    txt = re.sub(r"(\d+) *deg(\.|rees|s)?", r"\1{deg}", txt, flags=re.IGNORECASE)
    return txt


def roman_numerals(num) -> str:
    val = [1000, 900, 500, 400,  100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def num_to_words(num):
    '''Convert an integer between 1-99 into words'''
    if num < 0 or num > 99:
        return None
    units = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    teens = ['', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',  'seventeen', 'eighteen', 'nineteen']
    tens = ['', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',  'eighty', 'ninety']
    words = []
    if num == 0:
        words.append('zero')
    else:
        numStr = '%d' % num
        numStr = numStr.zfill(2)
        t, u = int(numStr[0]), int(numStr[1])
        if t > 1:
            words.append(tens[t])
            if u >= 1:
                words.append(units[u])
        elif t == 1:
            if u >= 1:
                words.append(teens[u])
            else:
                words.append(tens[t])
        else:
            if u >= 1:
                words.append(units[u])
    return ' '.join(words)

