import pytest
from source.manuscript_utils import (
    # adoc_renumber_chapters,
    fix_scene_breaks, quote_notate)


def test_quote_notate():
    assert quote_notate("So there! -- Anonymous") == """[quote, Anonymous]
____________________________________________________________________________
So there!
____________________________________________________________________________
"""
    assert quote_notate('"So there!" ~ Anonymous') == """[quote, Anonymous]
____________________________________________________________________________
So there!
____________________________________________________________________________
"""
    assert quote_notate("'So there!' - Anonymous") == """[quote, Anonymous]
____________________________________________________________________________
So there!
____________________________________________________________________________
"""


def scene_context(scene_break):
    return "This is the end of the prior scene.\n" + scene_break + "\nThis is the start of the next scene."


def test_fix_scene_breaks():
    proper = scene_context("'''")
    assert fix_scene_breaks(scene_context("---")) == proper
    assert fix_scene_breaks(scene_context("***********")) == proper
    assert fix_scene_breaks(scene_context("@@@@@@@@@@@")) == proper
    assert fix_scene_breaks(scene_context("#")) == proper
    assert fix_scene_breaks(scene_context("^^")) == proper
    assert fix_scene_breaks(scene_context("____")) == proper
    assert fix_scene_breaks(scene_context(".....")) == proper
    assert fix_scene_breaks(scene_context("=")) == proper
    assert fix_scene_breaks(scene_context("+++")) == proper
    assert fix_scene_breaks(scene_context("~~~~")) == proper
    assert fix_scene_breaks(scene_context("- - -")) == proper
    assert fix_scene_breaks(scene_context("**  **  **  **  **")) == proper
    assert fix_scene_breaks(scene_context(" @ @ @ @ @ @ @ @ @ @ @ ")) == proper
    assert fix_scene_breaks(scene_context(" # ")) == proper
    assert fix_scene_breaks(scene_context("^ ^")) == proper
    assert fix_scene_breaks(scene_context("_ _ _ _")) == proper
    assert fix_scene_breaks(scene_context(". . .")) == proper
    assert fix_scene_breaks(scene_context("+ + +")) == proper
    assert fix_scene_breaks(scene_context("~ ~ ~ ~")) == proper


# FIXME Missing unit test for adoc_renumber_chapters
# def test_adoc_renumber_chapters():
#     assert adoc_renumber_chapters() == ""


def main():
    pytest.main([__file__])


if __name__ == '__main__':
    main()
