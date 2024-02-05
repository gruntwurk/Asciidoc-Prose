import sublime, sublime_plugin  # noqa
# from dataclasses import dataclass
import re
import random
from datetime import datetime
from pathlib import Path
from .prose_utils import *
from .abstract_command import AbstractUtilTextCommand

# TODO use the actual package config facilities
STORY_GENERATOR_TEMPLATE = 'story_generator.adoc'


# ###########################################################################
# Story Generator Helpers
# ###########################################################################

class StoryChoices():
    def __init__(self, config_lines):
        self.config_lines = config_lines
        self.lists = {}
        self.list_name_for_prompt = {}
        self.template_lines = []
        self.load_all()

    def _list_by_name(self, name):
        return self.lists[name]

    def load_all(self):
        current_list = []
        list_name = ""
        lines = []
        for line in self.config_lines:
            line = line.rstrip()

            # Ignore comments
            if line.startswith('//'):
                continue

            # A block anchor marks the start of a list
            m = re.match(r"\[\[(.*)\]\]",line)
            if m:
                list_name = m.group(1)
                current_list = []
                self.lists[list_name] = current_list
                continue

            # Load the current list
            # Only preserve blank lines in the template
            if (list_name == "template") or line:
                current_list.append(line)

        self.examine_template(self.lists["template"])

    def parse_template_element(self, line):
        prompt = None
        list_name = None
        m = re.search(r"\* ([^<]+)<<(.+?)>>", line)
        if m:
            prompt = m.group(1).rstrip()
            list_name = m.group(2).rstrip()
        return (prompt, list_name)

    def examine_template(self, template_lines):
        self.template_lines = template_lines
        for line in self.template_lines:
            (prompt, list_name) = self.parse_template_element(line)
            if list_name:
                self.list_name_for_prompt[prompt] = list_name

    def generate_one_element(self, item, prompt) -> str:
        list = self.lists[item]
        return "* {} {}".format(prompt, list[random.randint(1, len(list))-1])


# ###########################################################################
# Story Generator Command
# ###########################################################################

class StoryGeneratorCommand(AbstractUtilTextCommand):
    def __init__(self, view):
        self.view = view
        self.template_name = None

    def _run(self):
        self.dispatch()

    def load_config(self, template_name = STORY_GENERATOR_TEMPLATE):
        self._load_config_contents(template_name)

        # Template
        self.template = "\n".join(self._get_config_block("template"))

    def dispatch(self):
        self._expand_selected_text_to_whole_lines()
        region = self.view.sel()[0]
        # print (">>{}<<".format(key))
        if self.generate_all(region):
            return
        if self.regenerate_partial(region):
            return

    def generate_all(self, region) -> bool:
        key = self.view.substr(region)
        # print("Attempting Gen All")
        """
        If the key (the currently selected text) is empty, then we're generating a whole new story.
        """
        m = re.match(r"// template: (.*)",key,flags=re.IGNORECASE)
        if m:
            self.template_name = m.group(1)
        elif key:
            return False
        if not self.template_name:
            self._replace_selected_text("// template: {}\n".format(STORY_GENERATOR_TEMPLATE))

        self.load_config(self.template_name)
        self.choices = StoryChoices(self.config_lines)

        story = ["","","// template: {}".format(self.template_name)]
        for line in self.choices.template_lines:
            (prompt, list_name) = self.choices.parse_template_element(line)
            if list_name:
                story.append(self.choices.generate_one_element(list_name, prompt))
            else:
                story.append(line)
        self._unselect()
        self._replace_selected_text(region,"\n".join(story))
        self._unselect()
        return True

    def regenerate_partial(self, region):
        old_text = self.view.substr(region)
        """
        If the key (the currently selected text) is not empty, then we're regenerating that element(s).
        """
        # print("Attempting Regen")
        if not self.template_name:
            return False
        if not old_text:
            return False
        old_lines = old_text.splitlines()
        new_lines = []
        for old_line in old_lines:
            m = re.match(r"\* ([a-z /]*:)", old_line.rstrip(), flags=re.IGNORECASE)
            if m:
                prompt = m.group(1).rstrip()
                list_name = self.choices.list_name_for_prompt[prompt]
                new_line = self.choices.generate_one_element(list_name, prompt)
                new_lines.append(new_line)
            else:
                new_lines.append(old_line)
        self._replace_selected_text(region,"\n".join(new_lines))
        # (leave selected)
        return True


