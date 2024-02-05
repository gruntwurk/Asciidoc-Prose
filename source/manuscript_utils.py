"""
Utility code for writing manuscripts in AsciiDoc
"""
import re


def fix_scene_breaks(text) -> str:
    """
    In a freshly imported story, a line of all the same symbol is usually a scene break.
    This converts them all to an AsciiDoc horizontal rule (''').
    """
    return re.sub(r"^ *([-@#^*_.=+~'])(\1| )*$", "'''", text, flags=re.MULTILINE)


def quote_notate(text) -> str:
    """
    Converts a quote in the form of "Aaaa bbb ccc" -- John Q. Public to an
    AsciiDoc quote block. The attribution separator can be either one or two
    dashes, or one or two tildes (~). An m-dash does not need to be surrounded
    by spaces, but the others do. If there is no such separator, then the
    quote will be unattributed.
    """
    quote = ""
    previous_separator = ""
    attribution = ""
    # Find the last occurrence of a --/-/~ separator
    while True:
        m = re.match(r"(.*?)(--| ~ | ~~ | - )(.*)", text)
        if m:
            quote += previous_separator + m.group(1)
            previous_separator = m.group(2)
            text = m.group(3)
            continue
        break
    if quote:
        attribution = text
    else:
        quote = text

    quote = quote.strip()
    m = re.match(r"^([\"'])(.*?)\1", quote)
    if m:
        quote = m.group(2)

    return "[quote, "+ \
    attribution.strip() + \
    "]\n____________________________________________________________________________\n" + \
    quote.strip() + \
    "\n____________________________________________________________________________\n"


def adoc_renumber_chapters(txt):
    lines = txt.splitlines()
    result = []
    chapter_number = 0

    for line in lines:
        m = re.match(r"^== *(Chapter )?([^:]*)(.*)", line, flags=re.IGNORECASE)
        if m:
            chapter_prefix = m.group(1)
            chapter_prefix = chapter_prefix.title() if chapter_prefix else ""
            wrong_number = m.group(2)
            chapter_title = m.group(3)
            chapter_number += 1
            if wrong_number.isdigit():
                result.append("== {}{}{}".format(chapter_prefix,chapter_number,chapter_title))
            elif re.match(r"^[- a-z]+$", wrong_number, flags=re.IGNORECASE):
                result.append("== {}{}{}".format(chapter_prefix,num_to_words(chapter_number).title(),chapter_title))
            else:
                result.append(line)
        else:
            result.append(line)

    return "\n".join(result)
