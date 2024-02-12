import re
import pytest
from source.prose_utils import (
    camel_case, snake_case,
    collapse_whitespace,
    fix_fractions, fix_temperature_degrees,
    generate_valid_anchor_token,
    transpose,
    num_to_words, pluck_out_match, roman_numerals)


def test_collapse_whitespace():
    assert collapse_whitespace("") == ""
    assert collapse_whitespace("abc") == "abc"
    assert collapse_whitespace("abc ") == "abc"
    assert collapse_whitespace("abc   ") == "abc"
    assert collapse_whitespace("  abc   ") == " abc"
    assert collapse_whitespace("  abc    def   ") == " abc def"
    assert collapse_whitespace("  abc    def   ") == " abc def"
    assert collapse_whitespace("  abc             def   ") == " abc def"


def test_camel_case():
    assert camel_case("something") == "Something"
    assert camel_case("some_thing") == "SomeThing"
    assert camel_case("some thing") == "Some thing"
    assert camel_case("SomeThing") == "Something"
    assert camel_case("") == ""


def test_snake_case():
    assert snake_case("SomeThing") == "some_thing"
    assert snake_case("someThing") == "some_thing"
    assert snake_case("some_thing") == "some_thing"
    assert snake_case("something") == "something"
    assert snake_case("") == ""


def test_pluck_out_match():
    txt = "The quick brown fox jumped over the lazy dog."
    m = re.search(r'quick', txt)
    assert pluck_out_match(txt, m, "slow") == "The slow brown fox jumped over the lazy dog."


def test_roman_numerals():
    assert roman_numerals(1) == "I"
    assert roman_numerals(2) == "II"
    assert roman_numerals(3) == "III"
    assert roman_numerals(4) == "IV"
    assert roman_numerals(5) == "V"
    assert roman_numerals(6) == "VI"
    assert roman_numerals(7) == "VII"
    assert roman_numerals(8) == "VIII"
    assert roman_numerals(9) == "IX"
    assert roman_numerals(10) == "X"
    assert roman_numerals(20) == "XX"
    assert roman_numerals(21) == "XXI"
    assert roman_numerals(40) == "XL"
    assert roman_numerals(41) == "XLI"
    assert roman_numerals(90) == "XC"
    assert roman_numerals(91) == "XCI"
    assert roman_numerals(100) == "C"
    assert roman_numerals(101) == "CI"
    assert roman_numerals(500) == "D"
    assert roman_numerals(501) == "DI"
    assert roman_numerals(1000) == "M"
    assert roman_numerals(1001) == "MI"


def test_num_to_words():
    assert num_to_words(-1) is None
    assert num_to_words(100) is None
    assert num_to_words(0) == 'zero'
    assert num_to_words(1) == 'one'
    assert num_to_words(2) == 'two'
    assert num_to_words(3) == 'three'
    assert num_to_words(4) == 'four'
    assert num_to_words(5) == 'five'
    assert num_to_words(6) == 'six'
    assert num_to_words(7) == 'seven'
    assert num_to_words(8) == 'eight'
    assert num_to_words(9) == 'nine'
    assert num_to_words(10) == 'ten'
    assert num_to_words(11) == 'eleven'
    assert num_to_words(12) == 'twelve'
    assert num_to_words(13) == 'thirteen'
    assert num_to_words(14) == 'fourteen'
    assert num_to_words(15) == 'fifteen'
    assert num_to_words(16) == 'sixteen'
    assert num_to_words(17) == 'seventeen'
    assert num_to_words(18) == 'eighteen'
    assert num_to_words(19) == 'nineteen'
    assert num_to_words(20) == 'twenty'
    assert num_to_words(21) == 'twenty one'
    assert num_to_words(30) == 'thirty'
    assert num_to_words(31) == 'thirty one'
    assert num_to_words(40) == 'forty'
    assert num_to_words(41) == 'forty one'
    assert num_to_words(50) == 'fifty'
    assert num_to_words(51) == 'fifty one'
    assert num_to_words(60) == 'sixty'
    assert num_to_words(61) == 'sixty one'
    assert num_to_words(70) == 'seventy'
    assert num_to_words(71) == 'seventy one'
    assert num_to_words(80) == 'eighty'
    assert num_to_words(81) == 'eighty one'
    assert num_to_words(90) == 'ninety'
    assert num_to_words(91) == 'ninety one'


def test_fix_fractions():
    assert fix_fractions('1/2') == "{half}"


def test_fix_temperature_degrees():
    assert fix_temperature_degrees("123 degrees Fahrenheit") == "123{deg}F"
    assert fix_temperature_degrees("123 deg Fahrenheit") == "123{deg}F"
    assert fix_temperature_degrees("123 deg. Fahrenheit") == "123{deg}F"
    assert fix_temperature_degrees("123 degs Fahrenheit") == "123{deg}F"
    assert fix_temperature_degrees("123 degs F") == "123{deg}F"
    assert fix_temperature_degrees("123 degs F.") == "123{deg}F"
    assert fix_temperature_degrees("123 degs fahrenheit") == "123{deg}F"
    assert fix_temperature_degrees("123 degs centigrade") == "123{deg}C"
    assert fix_temperature_degrees("123 degs celsius") == "123{deg}C"
    assert fix_temperature_degrees("123 degs C") == "123{deg}C"
    assert fix_temperature_degrees("123 degs C.") == "123{deg}C"
    assert fix_temperature_degrees("123 degrees") == "123{deg}"

# FIXME Missing unit test for format_day_of_week
# def test_format_day_of_week():
#     assert format_day_of_week() == ""

# FIXME Missing unit test for format_long
# def test_format_long():
#     assert format_long() == ""

# FIXME Missing unit test for format_slug
# def test_format_slug():
#     assert format_slug() == ""

# FIXME Missing unit test for format_slug_with_time
# def test_format_slug_with_time():
#     assert format_slug_with_time() == ""

# FIXME Missing unit test for standardize_keywords
# def test_standardize_keywords():
#     assert standardize_keywords() == ""


def test_transpose():
    assert transpose('Jane gave it to John') == 'John gave it to Jane'
    assert transpose('right-half') == 'half-right'
    assert transpose('red green') == 'green red'
    assert transpose('cat in the hat') == 'hat in the cat'
    assert transpose('alpha-beta') == 'beta-alpha'
    assert transpose('alpha_beta') == 'beta_alpha'
    assert transpose('alpha___beta') == '__beta_alpha'


def test_generate_valid_anchor_token():
    assert generate_valid_anchor_token('Star Wars') == 'star-wars'
    assert generate_valid_anchor_token('Star Wars: A New Hope') == 'star-wars-a-new-hope'
    assert generate_valid_anchor_token('Star Wars: A New Hope (1977)') == 'star-wars-a-new-hope-1977'
    assert generate_valid_anchor_token('Star_Wars: A_New_Hope (1977)') == 'star_wars-a_new_hope-1977'
    assert generate_valid_anchor_token('"Star_Wars!": [A New Hope,+=/;] (1977)') == 'star_wars-a-new-hope-1977'


def main():
    pytest.main([__file__])


if __name__ == '__main__':
    main()
