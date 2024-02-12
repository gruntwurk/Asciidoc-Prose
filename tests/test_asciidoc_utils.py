import pytest
from source.asciidoc_utils import (
    auto_align_table_columns,
    classify_adoc_syntax,
    # opinionated_adoc_fixup, adoc_fixup, asciidoctor_syntax_fixup,
    # extract_headings,
    index_tag,
    # unwrap_paragraphs,
    remove_links)


def test_classify_adoc_syntax():
    assert classify_adoc_syntax('[[foo]]') == ('ANCHOR', None, 'foo')


def test_remove_links():
    assert remove_links("<<anchor,label>>") == "label"
    assert remove_links("See <<foo,foo>>, <<bar_baz,bar baz>>, or <<smith_john,John Smith>>.") \
        == "See foo, bar baz, or John Smith."


def test_auto_align_table_columns():
    assert auto_align_table_columns("""
|==
| a | bravo |c|d
| alpha | | charlie
|apple|bug| c | diamond | edge | | grape
|==
""") == """
|==
| a     | bravo | c       | d       |      |  |
| alpha |       | charlie |         |      |  |
| apple | bug   | c       | diamond | edge |  | grape
|==
"""
    assert auto_align_table_columns("""
|==
| a | bravo |c|d
| this is a long entry | | if the total line length will be greater than 80, then no padding is used around the pipe separators
|apple|bug| c | diamond | edge | | grape
|==
""") == """
|==
|a                   |bravo|c                                                                                                   |d      |    ||
|this is a long entry|     |if the total line length will be greater than 80, then no padding is used around the pipe separators|       |    ||
|apple               |bug  |c                                                                                                   |diamond|edge||grape
|==
"""


def test_index_tag():
    assert index_tag('') == ''
    assert index_tag('foo') == '(((foo)))'
    assert index_tag('(((foo)))') == '((foo))'
    assert index_tag('((foo))') == '(foo)'
    assert index_tag('(foo)') == 'foo'


def main():
    pytest.main([__file__])


if __name__ == '__main__':
    main()
