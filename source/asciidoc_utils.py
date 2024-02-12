"""
Utility code for manipulating AsciiDoc, in general, without regard to what the
AsciiDoc is being used for (whether it's journaling, manuscript writing,
whatever).
"""
import re
from .prose_utils import collapse_whitespace

ADOC_LINK = r"<<[-_A-Za-z0-9]+,([^>]*)>>"
ADOC_HEADING = r"^(={1,5})\s+(.*)$"
ADOC_BULLET = r"^(\*{1,5})\s+(.*)$"
ADOC_ORDERED = r"^(\.{1,5})\s+(.*)$"
ADOC_ANCHOR = r"^\[\[([-_A-Za-z0-9]+)\]\]$"
BLANK_OR_COMMENT = r"^ *(// .*)?$"
BYLINE = r"^by "


def classify_adoc_syntax(line: str):
    """
    A quick-and-dirty method to parse a specific line of AsciiDoc text.
    Returns a 3-tuple:
        the command
        the argument for the command, if any (e.g. the indent level)
        the value, if any
    """
    if m := re.match(ADOC_ANCHOR, line):
        return ("ANCHOR", None, m[1])

    if m := re.match(ADOC_HEADING, line):
        return ("HEADING", len(m[1]), m[2])

    if m := re.match(ADOC_BULLET, line):
        return ("BULLET", len(m[1]), m[2])

    if m := re.match(ADOC_ORDERED, line):
        return ("ORDERED", len(m[1]), m[2])

    if m := re.match(BLANK_OR_COMMENT, line):
        return ("WHITESPACE", None, None)

    if m := re.match(BYLINE, line):
        return ("BYLINE", None, line)

    return ("OTHER", None, line)


def adoc_fixup(txt: str) -> str:
    """
    These conversions conform to "the AsciiDoc way."

    NOTE: This method is called by opinionated_adoc_fixup, so either call it,
    or this, but not both.
    """

    txt = collapse_whitespace(txt)

    # Delete any IDs automatically inserted by PanDoc
    txt = re.sub(r"\[\[_.*]]", "", txt)

    # Shorten table delimiters
    txt = re.sub(r"\|==+", "|===", txt)

    # convert m-dashes to AsciiDoc syntax
    txt = re.sub(r"—", "--", txt)

    # Replace figure captions with id and title
    txt = re.sub(r"^Figure (\d+)\s?(.*)", "[[fig-\\1]]\n.\\2\n", txt)

    # Replace references to figures with asciidoc xref
    txt = re.sub(r"Figure (\d+)", "<<fig-\\1>>", txt)

    # Smarten dumb quotes (make them typographic)
    txt = re.sub(r"(^|[^a-z])'(em|do|tis|twas|til)\b", "\\1{rsquo}\\2", txt, flags=re.IGNORECASE + re.MULTILINE)
    txt = re.sub(r"^\"", '"`', txt, flags=re.MULTILINE)
    txt = re.sub(r'^_"', '"`_', txt, flags=re.MULTILINE)
    txt = re.sub(r' "', ' "`', txt)
    txt = re.sub(r'"_(\W*)$', '_`"\\1', txt, flags=re.MULTILINE)
    txt = re.sub(r'"(\W*)$', '`"\\1', txt, flags=re.MULTILINE)
    txt = re.sub(r'"([- .,!?])', '`"\\1', txt)
    txt = re.sub(r'"_([- .,!?])', '_`"\\1', txt)
    txt = re.sub(r"^'", "'`", txt, flags=re.MULTILINE)
    txt = re.sub(r" '", " '`", txt)
    txt = re.sub(r"'\n", "`'", txt)
    txt = re.sub(r"'([- .,!?])", "`'\\1", txt)

    txt = re.sub(r'``"', '`"', txt)
    txt = re.sub(r"``'", "`'", txt)

    # Undo smart quotes, making sure to distinguish a possessive apostrophe from a closing quote
    txt = re.sub(r'“', '"`', txt)
    txt = re.sub(r'”', '`"', txt)
    txt = re.sub(r"‘", "'`", txt)
    txt = re.sub(r"(\w)’(\w)", "\\1'\\2", txt)
    txt = re.sub(r"’", "`'", txt)

    # AsciiDoctor can't handle m-dashes at the end of a quotation.
    txt = re.sub(r' *-- *`"', '{mdash}`"', txt)
    return txt


def opinionated_adoc_fixup(txt: str) -> str:
    """
    These conversions are not universally used, but considered to be best practices by many.
    """
    # First, the mandatory cleanup
    txt = adoc_fixup(txt)

    # Now, apply certain best practices

    # Ensure bullet point syntax (exactly one space following)
    txt = re.sub(r"^(-+|\*+|\.+) *", "\\1 ", txt, flags=re.MULTILINE)

    # Ensure exactly one space before and after ellipses and m-dashes that are mid-sentence (between words)
    txt = re.sub(r"(\w) *\.\.\.+ *(\w)", "\\1 ... \\2", txt)
    txt = re.sub(r"(\w) *-- *(\w)", "\\1 -- \\2", txt)

    # Make sure all m-dashes are represented by exactly 2 dashes
    txt = re.sub(r" +-+ +", " -- ", txt)

    # Fix transposed end-of-quotation punctuation -- that is, the punctuation goes inside the quotes
    txt = re.sub(r'`"(,|\.|\?|\!)', "\\1`\"", txt)
    txt = re.sub(r"`'(,|\.|\?|\!)", "\\1`'", txt)

    # Fix misplaced commas near parentheticals
    txt = re.sub(r",( *\([^)]*?\))", "\\1,", txt)

    # One sentence per line -- allowing for closing quotes and closing italics
    txt = re.sub(r'(\.|\?|\!)(`?["\']?)(_?) +([^a-z])', "\\1\\2\\3\n\\4", txt)

    # Fix false line breaks after abbreviations, single initials and ellipses
    txt = re.sub(r'(Mrs?|Ms|Drs?|Prof|\baka|\bp|\badj|\bn|\bv|a\.k\.a|e\.g|\bvs|\best|i\.e|P\.O| [A-Z]| \.\.)\. *\n', '\\1. ', txt, flags=re.MULTILINE)

    # HTML Entities to Attributes
    txt = re.sub(r"&apos;", "{rsquo}", txt)
    txt = re.sub(r"&(\w*);", "{\\1}", txt)

    return txt


def asciidoctor_syntax_fixup(txt: str) -> str:

    def convert_heading(underline_char="=", prefix="= "):
        line_length = len(lines[lineno - 1])
        if line_length > 4 and lines[lineno] == underline_char * line_length:
            lines[lineno - 1] = prefix + lines[lineno - 1]
            lines[lineno] = ""

    # set aside scene breaks
    txt = re.sub(r"^'''+$", "--scene--break--goes--here--", txt, flags=re.MULTILINE)

    # typographic double-quote syntax
    txt = re.sub(r"^``([^`])", "\"`\\1", txt, flags=re.MULTILINE)
    txt = re.sub(r" ``([^`])", " \"`\\1", txt)
    txt = re.sub(r"([^'])''", "\\1`\"", txt)
    txt = re.sub(r'``"', '`"', txt)

    # # typographic single-quote syntax
    # txt = re.sub(r"^`([^`])", "'`\\1", txt, flags=re.MULTILINE)
    # txt = re.sub(r" `([^`])", " '`\\1", txt)
    # txt = re.sub(r"([^'])'([- .,!?])", "\\1`'\\2", txt)
    # txt = re.sub(r"``'", "`'", txt)

    # restore scene breaks
    txt = re.sub(r"^--scene--break--goes--here--$", "'''", txt, flags=re.MULTILINE)

    # AsciiDoctor can't handle m-dashes at the end of a quotation.
    txt = re.sub(r' *-- *`"', '{mdash}`"', txt)

    # Title/Headings
    lines = txt.splitlines()
    for lineno in range(1, len(lines)):
        convert_heading("=", "= ")
        convert_heading("-", "== ")
        convert_heading("~", "=== ")
        convert_heading("^", "==== ")
        convert_heading("+", "===== ")

    return "\n".join(lines)


def remove_links(old_text: str) -> str:
    """
    Remove AsciiDoc links ( "<<anchor,label>>" ==> "label" )
    """
    return re.sub(ADOC_LINK, "\\1", old_text, flags=re.MULTILINE)


def auto_align_table_columns(text: str) -> str:
    """
    Adjusts the spacing within the lines of a table so that the pipe separators
    all line up.
    """
    col_widths = []
    padding = ''

    def analyze(line):
        parts = line.split('|')
        for i, part in enumerate(parts[1:]):
            width = len(part.strip())
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], width)
            else:
                col_widths.append(width)

    def align(line):
        parts = line.split('|')
        aligned_text = ''
        for i in range(len(col_widths)):
            part = parts[i + 1].strip() if i < len(parts) - 1 else ''
            aligned_text += (
                f'|{padding}{part}' + ' ' * (col_widths[i] - len(part)) + padding
            )
        return aligned_text.rstrip()

    lines = text.split('\n')
    for line in lines:
        if line.startswith('|') and not line.startswith('|=='):
            analyze(line)
    col_count = len(col_widths)
    compressed_line_length = sum(col_widths) + col_count
    padding = ' ' if compressed_line_length < 80 - col_count * 2 else ''
    adjusted_lines = []
    for line in lines:
        if line.startswith('|') and not line.startswith('|=='):
            line = align(line)
        adjusted_lines.append(line)
    return '\n'.join(adjusted_lines)


def extract_headings(lines, use_bullets=True, use_links=True):
    """
    This does the work for the static ToC command.
    """
    contents = []
    current_anchor = ""
    seeking_byline = False
    for line in lines:
        command, argument, value = classify_adoc_syntax(line)
        indent_level = argument if argument is int else 0

        if command == "ANCHOR":
            current_anchor = value
            continue

        # If the line is a heading, add it to the ToC
        if command == "HEADING":
            markup = "*" * int(indent_level) + " " if use_bullets else ""
            heading_text = value
            if use_links and current_anchor:
                contents.append(f"{markup}<<{current_anchor},{heading_text}>>")
            else:
                contents.append(f"{markup} {heading_text}")
            current_anchor = ""
            seeking_byline = True
            continue

        # If the line is blank or a comment, then the current state (current_anchor, seeking_byline) is still relevant
        if command == "WHITESPACE":
            continue

        # The anchor must have pertained to something other than a heading, forget it
        current_anchor = ""

        # If the line immediately after a heading is a byline, then add it to the end of the last ToC entry
        if seeking_byline and command == "BYLINE":
            contents[-1] += f" {value}"
    return contents


def unwrap_paragraphs(txt):
    """
    In AsciiDoc, paragraphs are represented by text that (can) span multiple
    lines, and one or more blank lines designates the break between paragraphs.
    This function undoes that, combining the text of each paragraph onto a
    single line, leaving no blank lines.
    """
    paragraphs = []
    paragraph = []
    lines = txt.splitlines()
    for line in lines:
        if line := line.rstrip():
            paragraph.append(line)
        else:
            combined_paragraph = " ".join(paragraph)
            paragraph = []
            if combined_paragraph:
                paragraphs.append(combined_paragraph)
    if paragraph:
        paragraphs.append(" ".join(paragraph))
    return "\n".join(paragraphs)


def index_tag(identifier: str) -> str:
    """
    Encloses the selected text in triple-parenthesis (making it into an
    invisible AsciiDoc index tag). If the selected text is already enclosed in
    parenthesis, then instead the outer pair of parenthesis are removed.
    Thus, it will cycle among triple-parenthesis, double-parenthesis,
    single-parenthesis, and no parenthesis.
    """
    if not identifier:
        return ""
    tokens = re.match(r"^(\(?)(.*?)(\)?)$", identifier)
    return tokens[2] if tokens[1] else f"((({tokens[2]})))"


