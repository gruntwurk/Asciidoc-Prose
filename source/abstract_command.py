import sublime, sublime_plugin
from pathlib import Path
import re


# ###########################################################################
#                                                            Abstract Command
# ###########################################################################
class AbstractUtilTextCommand(sublime_plugin.TextCommand):
    """
    Abstract base class for a Sublime Text Command that works by interacting
    with the current text buffer (view) for most input and output (e.g. by
    replacing the current selection that contains some sort of a query, with
    the results of the query).
    """
    def run(self, edit):
        self._edit = edit
        self._run()

    def find_local_file(self, filename) -> Path:
        """
        Search for the given file by name in one of these places:
        - The directory of the file being edited (if known)
        - The parent directory of the file being edited (if known)
        - All of the folders currently open in Sublime Text
        - The system's current directory
        - The sublime package directory where this command code resides
        """
        possible_locations = []
        if self.view.file_name():
            current_file_dir = Path(self.view.file_name()).parent.resolve()
            possible_locations.append(current_file_dir)
            possible_locations.append(current_file_dir.parent.resolve())
        for folder in self.view.window().folders():
            possible_locations.append(Path(folder))
        possible_locations.append(Path())
        possible_locations.append(Path(__file__).parent.resolve())
        for test_path in possible_locations:
            result = (test_path / filename)
            if result.exists():
                return result
        sublime.error_message("Cannot find {} in {}".format(filename,possible_locations))
        return None

    def load_config_contents(self, config_filename):
        p = self.find_local_file(config_filename)
        if not p:
            return False
        self.config_lines = []
        with p.open() as f:
            self.config_lines = f.readlines()

    def get_config_block(self, section_name):
        """
        Returns a list of strings with the contents of the named section of the config file.
        A section starts with the section name, enclosed in square brackets, on a line by itself.
        It ends when another section name is found or the EOF is reached.

        AsciiDoc literal blocks (between two lines of 4 or more dashes) are ignored.
        """
        results = []
        inside_literal = False
        current_section = ""
        for line in self.config_lines:
            m = re.match(r"^\-{4,}$", line)
            if m:
                inside_literal = not inside_literal
                continue
            if not inside_literal:
                m = re.match(r"\[+(\w*)\]+", line)
                if m:
                    if results:
                        break
                    current_section = m.group(1)
                    continue
            if current_section == section_name:
                results.append(line.rstrip())
        return results

    def get_config_first_line(self, section_name) -> str:
        """
        Returns the first non-blank line in the section.
        """
        lines = self.get_config_block(section_name)
        for line in lines:
            if line:
                return line
        return ""

    def get_selected_text(self):
        """
        Returns a list of strings with the text in the selected region(s).
        If only one region is selected, it still returns a list (of one).
        """
        results = []
        for s in self.view.sel():
            results.append(self.view.substr(s))
        return results

    def nothing_selected(self) -> bool:
        s = self.view.sel()
        if len(s) > 1:
            return False
        return s[0].begin() == s[0].end()

    def select_whole_file(self):
        """
        Removes all current selections and then selects the whole buffer
        (essentially, Ctrl+A).

        :example:
            if self.nothing_selected():
                self.select_whole_file()

        """
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, self.view.size()))

    def expand_selected_text_to_whole_lines(self):
        """
        """
        new_selections = []
        for s in self.view.sel():
            new_selections.append(self.view.line(s))
        self.view.sel().clear()
        self.view.sel().add_all(new_selections)

    def expand_selected_text_to_whole_subsection(self, classifier):
        """
        Expands the selection to encompass the entire chapter/section/subsection.
        This includes any preamble to the heading line such as anchors and comments.
        """
        new_selections = []

        # Build a master ToC of sorts
        headings = self.view.find_all('^=+')
        print (headings)

        sections = []
        for heading in headings:
            p = self.start_of_preamble(heading.begin(), classifier)
            sections.append( (p, len(heading)) )
            print ("section start {} -> {} len = {}".format(heading.begin(), p, len(heading)))
        # Add a phantom extra heading at the end to denote the EOF
        sections.append( (self.view.size() + 1, 0) )

        # Expand each current selection according to the ToC
        for s in self.view.sel():
            subsection_start = s.begin()
            subsection_end = s.end()
            subsection_level = 1
            for section_start, heading_level in sections:
                if section_start <= s.begin():
                    subsection_start = section_start
                    subsection_level = heading_level
                    continue
                if heading_level > subsection_level:
                    continue
                subsection_end = section_start - 1
                break
            new_selections.append(sublime.Region(subsection_start, subsection_end))

        self.view.sel().clear()
        self.view.sel().add_all(new_selections)

    def start_of_preamble(self, heading_begin, classifier):
        delineation_pt = heading_begin
        # Search backwards for the first non-preamble line above the heading line
        while delineation_pt > 0:
            possible_preamble_line = self.view.substr(self.view.full_line(delineation_pt - 1))
            classification, _ , _ = classifier(possible_preamble_line)
            print(classification)
            if classification not in ('ANCHOR', 'WHITESPACE'):
                break
            delineation_pt -= len(possible_preamble_line)
        return delineation_pt

    def get_file_content(self):
        """
        Returns the text in the entire buffer (without changing any selected
        regions).
        """
        return self.view.substr(sublime.Region(0, self.view.size()))

    def update_file(self, doc):
        """
        Clears the entire buffer and replaces it with the value of doc.
        doc can be a single str or a list of str.
        """
        if type(doc) is list:
            doc = "\n".join(doc)
        doc += "\n"
        self.unselect()
        self.view.replace(self._edit, sublime.Region(0, self.view.size()), doc)
        self.view.show(self.view.size(),keep_to_left=True)

    def replace_selected_text(self, region, doc):
        """
        Replaces the text of the given region (selection) with the value of doc.
        :param doc: a single str or a list of str.
        """
        if type(doc) is list:
            doc = "\n".join(doc)
        # print ("Replacing {}-{} with {} bytes".format(region.a, region.b, len(doc)))
        self.view.replace(self._edit, region, doc)
        self.view.show(region.a,keep_to_left=True)

    def process_all_regions(self, process_callback, as_snippet=False, unselect_after=False):
        """
        The given callback function is applied to all of the selected region(s),
        one at a time. The current contents of the region are passed into the
        function and then replaced with whatever the function returns.

        :param callback: A Callable that takes a single str and returns a str.

        :param as_snippet: If `as_snippet` is True AND there is only one
        region, then that result is executed as a snippet.

        :param unselect_after: Whether or not to leave the updated selection(s)
        selected, or clear them and leave the cursor at the end of the first
        selection. (Irrelevant if `as_snippet` if True.)
        """
        region_count = len(self.view.sel())
        for i, region in enumerate(self.view.sel()):
            self.view.window().status_message("Processing region {} of {}".format(i, region_count))
            original_text = self.view.substr(region)
            new_text = process_callback(original_text)
            if as_snippet and region_count == 1:
                self.replace_selected_text(region, "")
                self.view.run_command("insert_snippet", {"contents": new_text})
            else:
                self.replace_selected_text(region, new_text)
                if unselect_after:
                    self.unselect()

    def process_whole_file(self, process_callback):
        """
        Clears all current selections, then runs the callback function against
        the entire buffer.
        """
        self.view.sel().clear()
        self.update_file(process_callback(self.get_file_content()))

    def unselect(self, new_location="SAME"):
        """
        Clears the current selection(s), then sets the cursor to where the (first) selection ended.
        """
        s = self.view.sel()
        if new_location == "SOF":
            pt = 0
        elif new_location == "EOF":
            pt = self.view.size()
        else:
            pt = s[0].end()

        s.clear()
        s.add(sublime.Region(pt,pt))
        self.view.show(pt,keep_to_left=True)

