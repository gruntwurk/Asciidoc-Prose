import sublime
import sublime_plugin  # noqa
import re
from .source.prose_utils import (camel_case, collapse_whitespace,
                                 pluck_out_match, snake_case, transpose,
                                 generate_valid_anchor_token)
from .source.asciidoc_utils import (classify_adoc_syntax, remove_links,
                                    auto_align_table_columns, extract_headings,
                                    opinionated_adoc_fixup, unwrap_paragraphs,
                                    asciidoctor_syntax_fixup, index_tag)
from .source.cookbook_utils import (recipe_fixup)
from .source.journal_utils import (format_long, format_slug_with_time,
                                   standardize_keywords, journal_entry)
from .source.manuscript_utils import (adoc_renumber_chapters, fix_scene_breaks,
                                      quote_notate)
from .source.abstract_command import AbstractUtilTextCommand


# ###########################################################################
#                                                    Static Table of Contents
# ###########################################################################

class StaticTableOfContentsCommand(AbstractUtilTextCommand):
    """
    Inserts, at the top of the buffer, an unordered list corresponding
    to every heading in the current document.
    """

    def _run(self):
        contents = extract_headings(self.get_file_content().splitlines())
        self.unselect("SOF")
        self.replace_selected_text(sublime.Region(0, 0), "\n".join(contents) + "\n\n")


# ###########################################################################
#                                                           Renumber Chapters
# ###########################################################################

class AsciidocRenumberChaptersCommand(AbstractUtilTextCommand):
    """
    Renumbers all chapter headings.
    For example, if you have
        ...
        == Chapter Nine: Saving the Cat
        == Chapter Ten: The Mirror Moment
        == Chapter Eleven: Hero Status Achieved
        ...
    and you insert a new chapter between Ten and Eleven (== Chapter X: A Stumbling Block)
    then renumbering will get you:
        ...
        == Chapter Nine: Saving the Cat
        == Chapter Ten: The Mirror Moment
        == Chapter Eleven: A Stumbling Block
        == Chapter Twelve: Hero Status Achieved
        ...
    It also works for all of the following formats:
        == Chapter 9: Saving the Cat
        == Nine: Saving the Cat
        == 9: Saving the Cat
        == Chapter 9
        == Nine
        == 9
    Whatever format it finds, it will replicate.
    """

    def _run(self):
        self.process_whole_file(adoc_renumber_chapters)


# ###########################################################################
#                                                  Select All Spelling Errors
# ###########################################################################

class SelectAllSpellingErrorsCommand(sublime_plugin.TextCommand):
    """
    Clears any current selections, and then selects every spelling error in the
    current document. Useful for analyzing commonly misspelled words,
    made-up character names, etc.
    """

    def run(self, edit):
        regions = []
        while True:
            self.view.run_command('next_misspelling')
            mispell = self.view.sel()[0]
            # FIXME -- what if there aren't any misspellings?
            if mispell in regions:
                break
            # FIXME -- why line start?
            if self.view.classify(mispell.a) & sublime.CLASS_LINE_START:
                regions.append(mispell)
        self.view.sel().clear()
        self.view.sel().add_all(regions)


# ###########################################################################
#                                                              Select Section
# ###########################################################################

class AsciidocSelectSection(AbstractUtilTextCommand):
    """
    Expands the selection to encompass the entire chapter, section, or subsection.
    That is, the selection is first expanded upwards until it hits a heading line
    (= Title, == Chapter, === Section,etc.). Any preamble to the heading line,
    such as anchors and comments, are also included.

    The selection is then expanded downwards until it hits a corresponding
    heading at the same level, or one at a more significant level, or the end
    of the file.

    Works with multi-select.
    """

    def run(self, edit):
        self.expand_selected_text_to_whole_subsection(classify_adoc_syntax)


# ###########################################################################
#                                                                       Fixup
# ###########################################################################

class AsciidocProseFixupCommand(AbstractUtilTextCommand):
    """
    Cleans up a document that has been converted to AsciiDoc, e.g. by PanDoc...

    pandoc --from=docx --to=asciidoc --wrap=none --atx-headers --extract-media=extracted-media $FILENAME.docx > $FILENAME..adoc

    """

    def _run(self):
        if self.nothing_selected():
            self.select_whole_file()
        self.process_all_regions(opinionated_adoc_fixup)


class AsciidocUpdateSyntaxCommand(AbstractUtilTextCommand):
    """
    Cleans up old-style AsciiDoc syntax to the AsciiDoctor flavor.

    * Changes underlined title/headings to = prefixes
    * Changes `` '' quotations to "` `"

    """

    def _run(self):
        if self.nothing_selected():
            self.select_whole_file()
        self.process_all_regions(asciidoctor_syntax_fixup)


# ###########################################################################
#                                                         Recipe Standardizer
# ###########################################################################

class RecipeStandardizerCommand(AbstractUtilTextCommand):
    """
    Adjusts a recipe that was copied and pasted from elsewhere to be more AsciiDoc friendly.
    """

    def _run(self):
        if self.nothing_selected():
            self.select_whole_file()
        self.process_all_regions(recipe_fixup)


# ###########################################################################
#                                                                Scene-Breaks
# ###########################################################################

class AsciidocSceneBreakFixupCommand(AbstractUtilTextCommand):
    """
    Converts all lines that look like a scene break to a horizontal rule (''')
    """

    def _run(self):
        self.process_all_regions(fix_scene_breaks)


# ###########################################################################
#                                                              Quote Notation
# ###########################################################################

class AsciidocQuoteNotationCommand(AbstractUtilTextCommand):
    """
    Converts the selection to a Quote Block. If it finds one or more m-dashes
    or tildes, it assumes that the attribution follows.
    """

    def _run(self):
        if self.nothing_selected():
            self.expand_selected_text_to_whole_lines()
        self.process_all_regions(quote_notate)


# ###########################################################################
#                                                                 Align Table
# ###########################################################################

class AsciidocAlignTable(AbstractUtilTextCommand):
    """
    Adjusts the spacing within the lines of a table so that the pipe separators
    all line up.
    """

    def _run(self):
        self.process_all_regions(auto_align_table_columns)


# ###########################################################################
#                                                                  Snake Case
# ###########################################################################

class SnakeCaseCommand(AbstractUtilTextCommand):
    def _run(self):
        self.process_all_regions(snake_case)


class CamelCaseCommand(AbstractUtilTextCommand):
    def _run(self):
        self.process_all_regions(camel_case)


# ###########################################################################
#                                                                   Transpose
# ###########################################################################

class TransposeCommand(AbstractUtilTextCommand):
    def _run(self):
        self.process_all_regions(transpose)


# ###########################################################################
#                                                                   Index Tag
# ###########################################################################

class IndexTagCommand(AbstractUtilTextCommand):
    def _run(self):
        self.process_all_regions(index_tag)


# ###########################################################################
#                                                                 Link/Unlink
# ###########################################################################

class AsciidocLinkify(sublime_plugin.TextCommand):
    """
    Coverts the selected text to an AsciiDoc link.
    "Apple Pie" -> <<apple-pie,Apple Pie>>
    Works with multiple selections.
    """

    def run(self, edit):
        self._edit = edit
        for i, region in enumerate(self.view.sel()):
            link_text = self.view.substr(region).strip()
            if len(link_text) == 0:
                continue
                # TODO expand selection to word
            block_id = generate_valid_anchor_token(link_text)
            self.view.replace(self._edit, region, f"<<{block_id},{link_text}>>")


class AsciidocAnchorify(sublime_plugin.TextCommand):
    """
    Generates an AsciiDoc anchor according to the selected text.
    "Apple Pie" -> [[apple-pie]] (on the line above).
    Works with multiple selections.
    """

    def run(self, edit):
        self._edit = edit
        for i, region in enumerate(self.view.sel()):
            link_text = self.view.substr(region).strip()
            if len(link_text) == 0:
                continue
                # TODO expand selection to word
            whole_line_region = self.view.line(region)
            whole_line_text = self.view.substr(whole_line_region)
            block_id = generate_valid_anchor_token(link_text)
            self.view.replace(self._edit, whole_line_region, f'[[{block_id}]]\n{whole_line_text}')


class RemoveLinksCommand(AbstractUtilTextCommand):
    def _run(self):
        self.process_all_regions(remove_links)


# ###########################################################################
#                                                           Unwrap Paragraphs
# ###########################################################################

class UnwrapParagraphsCommand(AbstractUtilTextCommand):
    """
    In AsciiDoc, paragraphs are represented by text that (can) span multiple
    lines, and one or more blank lines designates the break between paragraphs.
    This command undoes that, combining the text of each paragraph onto a
    single line, leaving no blank lines.
    """

    def _run(self):
        self.expand_selected_text_to_whole_lines()
        self.process_all_regions(unwrap_paragraphs)


# ###########################################################################
#                                                            Convert From RST
# ###########################################################################

class AsciidocFromRstCommand(AbstractUtilTextCommand):
    """
    A quick-and-dirty start to converting RST markup to AsciiDoc
    """
    FOOTNOTE_PATTERN = r"^\.\. +_([^:]*): +(https?://[^\[\s]*)"
    VARIABLE_PATTERN = r"^\.\. +\|([^\|]*)\| +replace:: +(.*)$"

    def _run(self):
        self.expand_selected_text_to_whole_lines()
        self.process_all_regions(self.from_rst)

    def from_rst(self, txt: str) -> str:
        txt = collapse_whitespace(txt)

        # Gather footnoted http links
        footnotes = {}
        rst_footnotes = re.findall(self.FOOTNOTE_PATTERN, txt, flags=re.MULTILINE)
        for rst_footnote in rst_footnotes:
            ref, link = rst_footnote
            footnotes[ref] = link
        txt = re.sub(self.FOOTNOTE_PATTERN, "", txt, flags=re.MULTILINE)

        # Gather variables
        variables = {}
        rst_variables = re.findall(self.VARIABLE_PATTERN, txt, flags=re.MULTILINE)
        for rst_variable in rst_variables:
            name, definition = rst_variable
            variables[name] = definition
        txt = re.sub(self.VARIABLE_PATTERN, "", txt, flags=re.MULTILINE)

        # --- The following conversions can be done en masse ---

        # Monospaced
        txt = re.sub(r"``(.*?)``", '`\\1`', txt)

        # Anchor
        txt = re.sub(r"^\.\. +\[#(\w+)\] ", "[[\\1]]\n", txt, flags=re.MULTILINE)

        # Link to anchor
        txt = re.sub(r"`(.*?)`_ \[#(.*?)\]_", "<<\\2,\\1>>", txt)

        # Variable references
        while True:
            m = re.search(r"\|(.*?)\|", txt)
            if m:
                ref = m.group(1).replace("\n", " ")
                if ref in variables:
                    proper_ref = ref.replace(" ", "_")
                    txt = pluck_out_match(txt, m, "{" + proper_ref + "}")
                else:
                    txt = pluck_out_match(txt, m, ref)
            else:
                break

        # Link to footnoted http link
        while True:
            m = re.search(r"`([^`]*?)`_", txt)
            if m:
                ref = m[1].replace("\n", " ")
                if ref in footnotes:
                    txt = pluck_out_match(txt, m, footnotes[ref] + "[" + ref + "]")
                else:
                    txt = pluck_out_match(txt, m, ref)
            else:
                break

        while True:
            m = re.search(r"\b(\w*)_\b", txt)
            if m:
                ref = m.group(1)
                if ref in footnotes:
                    txt = pluck_out_match(txt, m, footnotes[ref] + "[" + ref + "]")
                else:
                    txt = pluck_out_match(txt, m, ref)
            else:
                break

        # TODO Comments
        txt = re.sub(r"^\.\. +todo::", "// TODO ", txt, flags=re.MULTILINE)

        # Comments
        txt = re.sub(r"^\.\. +<--(.*?)-->", "// \\1 ", txt, flags=re.MULTILINE)

        # Ordered lists
        txt = re.sub(r"^#\. ", ". ", txt, flags=re.MULTILINE)

        # Footnoted http link
        txt = re.sub(r"^\.\. +_([^:]*): +(https?://[^\[\s]*)", "[[\\1]]\n\\2[\\1]", txt, flags=re.MULTILINE)

        # --- The following conversions need to be done line-by-line ---
        lines = txt.splitlines()
        current_anchor = ""
        seeking_byline = False
        for i, line in enumerate(lines):

            # H2
            m = re.match(r"^(=+)$", line)
            if m and i > 0:
                previous_line = lines[i - 1]
                if len(previous_line) == len(line):
                    lines[i - 1] = "== " + previous_line
                    lines[i] = ""

            # H3
            m = re.match(r"^(-+)$", line)
            if m and i > 0:
                previous_line = lines[i - 1]
                if len(previous_line) == len(line):
                    lines[i - 1] = "=== " + previous_line
                    lines[i] = ""

        txt = "\n".join(lines)

        # --- More conversions that can be done en masse ---

        # Double-colons
        txt = re.sub(r":: *$", ":", txt, flags=re.MULTILINE)

        if variables:
            txt = "\n".join([":{}: {}".format(ref.replace(" ", "_"), variables[ref]) for ref in variables]) + "\n\n" + txt

        return txt

# ###########################################################################
#                                                               Journal Entry
# ###########################################################################


class JournalEntryCommand(AbstractUtilTextCommand):
    def _run(self, **kwargs):
        self.expand_selected_text_to_whole_lines()
        self.process_all_regions(journal_entry, as_snippet=True, unselect_after=True, **kwargs)


# ###########################################################################
#                                                              Dropped Images
# ###########################################################################

class AsciidocGatherDroppedImagesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self._edit = edit
        filenames = self._gather_images()
        results = [f"image::{f}[]" for f in filenames]
        self._replace_selected_text(results)
        self._unselect()

    def _replace_selected_text(self, doc):
        if type(doc) is list:
            doc = "\n".join(doc)
        doc += "\n"
        self.view.replace(self._edit, self.view.sel()[0], doc)

    def _unselect(self):
        s = self.view.sel()
        pt = s[0].end()
        s.clear()
        s.add(sublime.Region(pt, pt))

    def _gather_images(self) -> list:
        results = []
        for sheet in self.view.window().sheets():
            if (type(sheet) is sublime.ImageSheet):
                results.append(sheet.file_name())
                sheet.close()
        return results
