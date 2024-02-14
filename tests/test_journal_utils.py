import pytest
from datetime import datetime
from source.journal_utils import (
    format_day_of_week, format_long,
    format_slug, format_slug_with_time,
    journal_entry, standardize_keywords,
    INSIGNIFICANT_WORDS)

VALENTINES_DAY_NEAR_MIDNIGHT = datetime(2024, 2, 14, 23, 59)


def test_format_day_of_week():
    assert format_day_of_week(VALENTINES_DAY_NEAR_MIDNIGHT) == 'Wednesday'


def test_format_long():
    assert format_long(VALENTINES_DAY_NEAR_MIDNIGHT) == '14 February 2024 Wednesday'


def test_format_slug():
    assert format_slug(VALENTINES_DAY_NEAR_MIDNIGHT) == '2024-02-14'


def test_format_slug_with_time():
    assert format_slug_with_time(VALENTINES_DAY_NEAR_MIDNIGHT) == '2024-02-14-2359'


def test_journal_entry():
    assert journal_entry(subject='The Girl with a Big Heart', offset=None, reference_date=VALENTINES_DAY_NEAR_MIDNIGHT) == '''


[[entry-2024-02-14-2359]]
== 14 February 2024 Wednesday: The Girl with a Big Heart

(((girl))) (((big))) (((heart)))

'''

    assert journal_entry(subject='The Girl with a Big Heart', offset=0, reference_date=VALENTINES_DAY_NEAR_MIDNIGHT) == '''


[[entry-2024-02-14]]
== 14 February 2024 Wednesday: The Girl with a Big Heart

(((girl))) (((big))) (((heart)))

'''

    assert journal_entry(subject='The Girl with a Big Heart', offset=1, reference_date=VALENTINES_DAY_NEAR_MIDNIGHT) == '''


[[entry-2024-02-13]]
== 13 February 2024 Tuesday: The Girl with a Big Heart

(((girl))) (((big))) (((heart)))

'''


def test_standardize_keywords():
    words = "The Girl with a Big Heart".split()
    assert words == ['The', 'Girl', 'with', 'a', 'Big', 'Heart']
    assert standardize_keywords(words, {'': INSIGNIFICANT_WORDS}) == ['girl', 'big', 'heart']


def main():
    pytest.main([__file__])


if __name__ == '__main__':
    main()
